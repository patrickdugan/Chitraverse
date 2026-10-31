from __future__ import annotations
import json
import re
import sqlite3
from collections import Counter
from contextlib import closing
from pathlib import Path
from .core import canonical, digest, now, rows, write_json


def label(row):
    return row.get('title') or row.get('name') or row.get('title_hint') or row.get('index_label') or row['url']


def clean(text):
    return str(text or '').replace('|', '\\|').replace('\n', ' ')


def report(root):
    pubs = rows(root / 'catalog/publications.jsonl')
    papers = rows(root / 'catalog/papers.jsonl')
    appearances = rows(root / 'catalog/appearances.jsonl')
    transcripts = rows(root / 'catalog/transcripts.jsonl')
    tweets = rows(root / 'catalog/tweets.jsonl')
    tweet_candidates = rows(root / 'catalog/tweet-candidates.jsonl')
    acquisitions = rows(root / 'catalog/acquisition.jsonl')
    confirmed = [r for r in appearances if r.get('participation') == 'confirmed']
    primary = [r for r in papers if r.get('relationship') in {'author_verified_arxiv', 'personal_site_linked_artifact'}]
    def present(r):
        return bool(r.get('text_path')) and (root / r['text_path']).is_file()
    stored_publications = sum(present(p) for p in pubs)
    stored_papers = sum(present(p) for p in primary)
    stored_transcripts = sum(present(t) for t in transcripts)
    coverage = {
      'generated_at': now(), 'writing_source_records': len(pubs), 'writing_texts_stored': stored_publications,
      'authored_or_personal_site_papers': len(primary), 'paper_texts_stored': stored_papers,
      'other_paper_or_citation_records': len(papers) - len(primary),
      'appearance_source_records': len(appearances), 'confirmed_appearance_source_records': len(confirmed),
      'confirmed_transcript_records': stored_transcripts, 'transcripts_requiring_review': sum(t.get('quality') == 'unverified' for t in transcripts),
      'tweet_records': len(tweets), 'tweet_candidates': len(tweet_candidates), 'tweet_full_text_files_stored': sum(present(t) for t in tweets),
      'acquisition_failures': sum(a.get('status') == 'failed' for a in acquisitions),
      'exhaustive_coverage_established': False,
      'limits': [
        'Personal-site discovery is bounded to linked pages and the site sitemap; an unindexed page may be missing.',
        'ArXiv author records are matched against the exact author name; cited works are not counted as authored papers.',
        'Podcast and interview source URLs can describe the same event; URL counts are not event counts.',
        'Tweet collection requires an X API bearer token. Without it, the public timeline cannot be scanned through the official API.',
        'X API availability and retention can omit older posts even with credentials; the report does not claim a complete historical archive.',
        'Full publisher texts, transcripts, and tweet text remain local and ignored by Git.',
        'Machine transcripts are unverified and do not infer speaker labels.',
        'No recurring collection schedule is installed.'
      ]
    }
    write_json(root / 'reports/coverage.json', coverage)
    # Preserve explicit access and identity review items while refreshing generated missing-artifact entries.
    existing = [r for r in rows(root / 'catalog/backlog.jsonl') if r.get('status') in {'credentials_required','review_required','publisher_access_challenge','scan_complete_for_available_api_window'}]
    backlog = list(existing)
    def add(url, reason):
      if not any(r.get('url') == url and r.get('reason') == reason for r in backlog): backlog.append({'url':url,'reason':reason})
    for p in pubs:
      if not present(p): add(p['url'], 'personal_page_text_missing')
    for p in primary:
      if not present(p): add(p['url'], 'paper_text_missing')
    done = {canonical(t['url']) for t in transcripts if present(t)}
    for a in confirmed:
      if canonical(a['url']) not in done and a.get('transcript_status') != 'publisher_version_available': add(a['url'],'confirmed_source_transcript_missing')
    for a in appearances:
      if a.get('participation') == 'review_required': add(a['url'],'participation_or_source_review')
    backlog_path = root / 'catalog/backlog.jsonl'
    backlog_path.write_text('', encoding='utf8')
    from .core import upsert
    upsert(backlog_path, backlog)
    lines = ['# Chitraverse coverage', '', f'Generated {coverage["generated_at"][:10]} UTC.', '',
      f'{stored_publications}/{len(pubs)} discovered writing sources have local text.',
      f'{stored_papers}/{len(primary)} authored or first-party linked paper artifacts have local text; {coverage["other_paper_or_citation_records"]} related records remain separate.',
      f'{len(appearances)} appearance source URLs, including {len(confirmed)} confirmed by publisher evidence.',
      f'{stored_transcripts} transcript texts are stored locally across {len(transcripts)} transcript records.',
      f'{len(tweets)} public posts are cataloged; {len(tweet_candidates)} indexed tweet candidates await official-account confirmation; {coverage["tweet_full_text_files_stored"]} local text copies are available.', '',
      '## Personal writing and papers', '', '| Type | Source | Date | Text |', '|---|---|---|---|']
    lines += [f'| {clean(p.get("kind", p.get("relationship", "page")))} | [{clean(label(p))}]({p["url"]}) | {clean(p.get("published"))} | {"stored" if present(p) else "missing"} |' for p in pubs + primary]
    lines += ['', '## Podcast and interview appearances', '', '| Source | Role | Participation | Transcript |', '|---|---|---|---|']
    transcript_by_url={canonical(t['url']):t for t in transcripts}
    lines += [f'| [{clean(label(a))}]({a["url"]}) | {clean(a.get("role"))} | {a.get("participation", "unknown")} | {transcript_by_url.get(canonical(a["url"]), {}).get("kind", a.get("transcript_status", "pending"))} |' for a in appearances]
    lines += ['', '## Tweets', '', 'The collector uses the official X API v2 timeline endpoint when `CHITRAVERSE_X_BEARER_TOKEN` is present. Tweet text is excluded from Git; record URLs, source metadata and checksums remain in the catalog. X API retention can limit historical completeness.', '', '## Coverage limits', '']
    lines += ['- ' + x for x in coverage['limits']]
    lines += ['', 'See `catalog/backlog.jsonl` for missing items and `catalog/acquisition.jsonl` for retrieval errors.']
    (root / 'reports/coverage.md').write_text('\n'.join(lines)+'\n', encoding='utf8')
    relations=[]
    for p in pubs:
      for target in p.get('outlinks',[]): relations.append({'subject':p['url'],'predicate':'links_source','object':target,'evidence_url':p['url'],'status':'observed_hyperlink'})
    rp=root/'ontology/relations.jsonl'; rp.parent.mkdir(parents=True,exist_ok=True)
    rp.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in relations),encoding='utf8')
    index(root)
    print(json.dumps(coverage,ensure_ascii=False,indent=2))


def index(root):
    db=root/'.cache/search.sqlite3'; db.parent.mkdir(parents=True,exist_ok=True)
    with closing(sqlite3.connect(db)) as conn, conn:
      conn.execute('DROP TABLE IF EXISTS documents')
      conn.execute('CREATE VIRTUAL TABLE documents USING fts5(title, source_url UNINDEXED, path UNINDEXED, text)')
      seen=set()
      for name in ['publications','papers','appearances','transcripts','tweets','tweet-candidates']:
        for r in rows(root/f'catalog/{name}.jsonl'):
          path=r.get('text_path')
          if not path or path in seen or not (root/path).exists(): continue
          seen.add(path)
          conn.execute('INSERT INTO documents VALUES (?,?,?,?)',(label(r),r['url'],path,(root/path).read_text(encoding='utf8',errors='replace')))


def search(root, query, limit=10):
    if not query: raise ValueError('--query is required')
    with closing(sqlite3.connect(root/'.cache/search.sqlite3')) as conn:
      matches=conn.execute("SELECT title, source_url, path, snippet(documents,3,'[',']',' … ',32) FROM documents WHERE documents MATCH ? ORDER BY rank LIMIT ?",(query,limit)).fetchall()
    for title,url,path,snippet in matches: print(json.dumps({'title':title,'source':url,'path':path,'excerpt':snippet},ensure_ascii=False))


def validate(root):
    errors=[]; checked=0
    for name in ['publications','papers','appearances','transcripts','tweets','tweet-candidates']:
      records=rows(root/f'catalog/{name}.jsonl'); urls=[r['url'] for r in records]
      if len(urls)!=len(set(urls)): errors.append(f'Duplicate keys in {name}')
      for r in records:
        for field,hash_field in [('text_path','text_sha256'),('segments_path',None)]:
          if not r.get(field): continue
          path=(root/r[field]).resolve()
          if not path.is_relative_to(root.resolve()): errors.append(f'Path outside corpus: {path}'); continue
          if not path.exists(): errors.append(f'Missing file: {path}'); continue
          if hash_field and digest(path.read_bytes())!=r.get(hash_field): errors.append(f'Hash mismatch: {path}')
          checked+=1
    result={'checked_local_files':checked,'errors':errors}; write_json(root/'reports/validation.json',result)
    print(json.dumps(result,ensure_ascii=False,indent=2))
    if errors: raise SystemExit(1)
