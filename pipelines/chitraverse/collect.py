from __future__ import annotations

import io
import json
import re
import urllib.parse
from pathlib import Path
from xml.etree import ElementTree as ET

from .core import (Fetcher, article, attempt, canonical, digest, links, now,
                   publication, rows, save_text, sitemap, title, upsert, write_json)

HOME = 'https://tarunchitra.com'


def discover(root, fetch):
    """Discover the personal-site archive and author-verified arXiv papers."""
    pages = set()
    for index in json.loads((root / 'config/sources.json').read_text(encoding='utf8'))['official_indexes']:
        index = canonical(index)
        if index.lower().endswith('.xml'):
            urls = attempt(root, 'personal_sitemap', index, lambda: sitemap(fetch, index)) or []
            pages.update(canonical(u) for u in urls)
            continue
        result = attempt(root, 'personal_index', index, lambda: fetch.html(index))
        if not result:
            continue
        soup, meta = result
        pages.add(canonical(meta['final_url']))
        for url in links(soup, meta['final_url']):
            if urllib.parse.urlsplit(url).hostname in {'tarunchitra.com', 'www.tarunchitra.com'}:
                if not re.search(r'\.(?:pdf|jpg|png|gif|css|js|xml)$', url, re.I):
                    pages.add(url)
                elif url.lower().endswith('.pdf'):
                    upsert(root / 'catalog/papers.jsonl', [{'url': url, 'relationship': 'personal_site_linked_artifact', 'discovered_from': index, 'authorship': 'unreviewed'}])
    # Author profile indexes are scanned by same-domain links, then each article's own byline is verified.
    for index in json.loads((root / 'config/sources.json').read_text(encoding='utf8')).get('writing_indexes', []):
        result = attempt(root, 'author_writing_index', index, lambda: fetch.html(index))
        if not result:
            continue
        soup, meta = result
        host = urllib.parse.urlsplit(meta['final_url']).hostname
        for url, label in links(soup, meta['final_url']).items():
            parsed = urllib.parse.urlsplit(url)
            if parsed.hostname == host and parsed.path not in {'', '/'} and not re.search(r'\.(?:jpg|png|gif|css|js|woff2?)$', parsed.path, re.I):
                upsert(root / 'catalog/publications.jsonl', [{'url': url, 'kind': 'personal_writing_candidate', 'index_label': label,
                       'discovered_from': meta['final_url'], 'authorship_status': 'verify_article_byline', 'status': 'discovered'}])
    # Restrict the personal-site crawl to its linked pages; external links remain relationships, not author claims.
    for url in sorted(pages):
        path = urllib.parse.urlsplit(url).path.lower()
        if any(x in path for x in ['/about', '/papers', '/blog', '/index', '/cv', '/contact']):
            upsert(root / 'catalog/publications.jsonl', [{'url': url, 'kind': 'personal_site_page', 'discovered_from': 'https://tarunchitra.com/', 'status': 'discovered'}])
    # Use arXiv's public Atom API. Exact author-list matches are retained separately from coauthor hits.
    query = 'au:"Tarun Chitra"'
    api = 'https://export.arxiv.org/api/query?' + urllib.parse.urlencode({'search_query': query, 'start': 0, 'max_results': 200, 'sortBy': 'submittedDate', 'sortOrder': 'ascending'})
    result = attempt(root, 'arxiv_author_search', api, lambda: fetch.get(api))
    verified = 0
    if result:
        feed = ET.fromstring(result[0])
        ns = {'a': 'http://www.w3.org/2005/Atom'}
        for item in feed.findall('a:entry', ns):
            authors = [a.findtext('a:name', default='', namespaces=ns).strip() for a in item.findall('a:author', ns)]
            paper_url = next((l.get('href') for l in item.findall('a:link', ns) if l.get('rel') == 'alternate'), None)
            if not paper_url:
                continue
            exact = any(re.sub(r'\s+', ' ', name).casefold() == 'tarun chitra' for name in authors)
            row = {'url': canonical(paper_url), 'relationship': 'author_verified_arxiv' if exact else 'coauthor_candidate',
                   'authors': authors, 'title': re.sub(r'\s+', ' ', item.findtext('a:title', default='', namespaces=ns)).strip(),
                   'abstract': re.sub(r'\s+', ' ', item.findtext('a:summary', default='', namespaces=ns)).strip(),
                   'published': item.findtext('a:published', default='', namespaces=ns),
                   'arxiv_id': item.findtext('a:id', default='', namespaces=ns).rsplit('/', 1)[-1],
                   'discovered_from': api, 'status': 'metadata_stored'}
            upsert(root / 'catalog/papers.jsonl', [row])
            if exact:
                verified += 1
    write_json(root / 'catalog/official-index.json', {'personal_site_pages': len(pages), 'arxiv_author_matches': verified, 'source': HOME, 'checked_at': now()})
    print(f'Personal-site pages discovered: {len(pages)}; exact arXiv author matches: {verified}', flush=True)


def paper_url(url):
    p = urllib.parse.urlsplit(url)
    if p.hostname in {'tarunchitra.com', 'www.tarunchitra.com'} and p.path.lower().endswith('.pdf'):
        return canonical(url)
    if p.hostname in {'arxiv.org', 'export.arxiv.org'}:
        match = re.search(r'/(?:abs|pdf|html)/(\d{4}\.\d{4,5}(?:v\d+)?)', p.path)
        if match:
            return 'https://arxiv.org/abs/' + re.sub(r'v\d+$', '', match.group(1))
    if p.hostname == 'doi.org':
        return canonical(url)
    return None


def collect_publications(root, fetch):
    for record in rows(root / 'catalog/publications.jsonl'):
        url = record['url']
        result = attempt(root, 'personal_page', url, lambda: fetch.html(url))
        if not result:
            continue
        soup, meta = result
        text = article(soup)
        found = links(soup, meta['final_url'])
        author_labels = sorted({a.get_text(' ', strip=True) for a in soup.select('a[rel=author], a[data-testid*=author], .pw-author') if a.get_text(' ', strip=True)})
        exact_author = any(a.casefold() == 'tarun chitra' for a in author_labels) or 'tarun chitra' in text[:1000].casefold()
        update = {**record, **save_text(root, 'private/publications', url, text, meta), 'title': title(soup),
                  'published': publication(soup), 'final_url': meta['final_url'], 'status': 'text_stored',
                  'author_labels': author_labels, 'authorship_status': 'byline_verified' if exact_author else record.get('authorship_status', 'review_byline'),
                  'outlinks': sorted(found), 'rights': 'Original source copyright; local research copy; redistribution not established'}
        upsert(root / 'catalog/publications.jsonl', [update])
        for target, label in found.items():
            paper = paper_url(target)
            if paper:
                relationship = 'personal_site_linked_artifact' if 'tarunchitra.com' in paper else 'linked_reference_authorship_unreviewed'
                upsert(root / 'catalog/papers.jsonl', [{'url': paper, 'label': label, 'discovered_from': url,
                       'relationship': relationship, 'authorship': 'listed_by_personal_site' if relationship == 'personal_site_linked_artifact' else 'unreviewed'}])
            if target.startswith('https://www.youtube.com/watch?v='):
                upsert(root / 'catalog/appearances.jsonl', [{'url': target, 'title_hint': label, 'discovered_from': url,
                       'participation': 'review_required', 'role': 'unknown'}])
        print(f'Personal page: {update["title"]}', flush=True)


def collect_repos(root, fetch):
    print('Repository scanning is out of scope; use the paper and appearance collectors.')


def collect_microsites(root, fetch):
    return


def collect_papers(root, fetch):
    from pypdf import PdfReader
    review_path = root / 'config/paper-reviews.json'
    if review_path.exists():
        upsert(root / 'catalog/papers.jsonl', json.loads(review_path.read_text(encoding='utf8')))
    for record in rows(root / 'catalog/papers.jsonl'):
        if record.get('relationship') not in {'author_verified_arxiv', 'personal_site_linked_artifact'}:
            continue
        url = record['url']
        result = attempt(root, 'paper', url, lambda: fetch.get(url))
        if not result:
            continue
        raw, meta = result
        if raw.startswith(b'%PDF'):
            try:
                text = '\n\n'.join(page.extract_text() or '' for page in PdfReader(io.BytesIO(raw)).pages)
            except Exception as exc:
                upsert(root / 'catalog/papers.jsonl', [{'url': url, 'status': 'downloaded_text_extraction_failed', 'error': str(exc)[:300]}])
                continue
            updated = {**record, **save_text(root, 'private/papers', url, text, meta), 'status': 'pdf_text_stored'}
        else:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(raw, 'html.parser')
            if any(s in title(soup).lower() for s in ['client challenge', 'just a moment', 'access denied']):
                updated = {**record, 'status': 'publisher_access_challenge'}
            else:
                updated = {**record, 'title': title(soup), 'status': 'metadata_stored', 'retrieved_at': meta['retrieved_at'], 'response_sha256': meta['sha256']}
                abstract = soup.select_one('.abstract')
                if abstract:
                    updated['abstract'] = abstract.get_text(' ', strip=True).removeprefix('Abstract: ')
                html_url = url.replace('/abs/', '/html/')
                html_result = attempt(root, 'paper_html', html_url, lambda: fetch.html(html_url)) if 'arxiv.org/abs/' in url else None
                if html_result:
                    html_soup, html_meta = html_result
                    updated.update(save_text(root, 'private/papers', url, article(html_soup), html_meta))
                    updated['status'] = 'html_text_stored'
        upsert(root / 'catalog/papers.jsonl', [updated])
        print(f'Paper: {updated.get("title", url)}', flush=True)
