from __future__ import annotations
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from .core import digest, now, rows, upsert, write_json

HANDLE = 'tarunchitra'
API = 'https://api.x.com/2'


def collect_tweets(root: Path, fetch, limit: int = 100):
    """Use X's authenticated v2 timeline API; never use unofficial mirrors."""
    profile = f'https://x.com/{HANDLE}'
    upsert(root / 'catalog/source-indexes.jsonl', [{'url': profile, 'kind': 'x_profile', 'handle': HANDLE,
           'identity_status': 'publisher_cross_reference_available_review_required', 'checked_at': now()}])
    seeds = json.loads((root / 'config/tweet-seeds.json').read_text(encoding='utf8'))
    for seed in seeds:
        upsert(root / 'catalog/tweet-candidates.jsonl', [seed])
    token = os.environ.get('CHITRAVERSE_X_BEARER_TOKEN')
    if not token:
        upsert(root / 'catalog/backlog.jsonl', [{'url': profile, 'kind': 'tweets', 'status': 'credentials_required',
               'detail': 'Complete timeline collection requires an X API bearer token in CHITRAVERSE_X_BEARER_TOKEN. No unofficial mirror or login workaround is used.'}])
        print('X timeline scan not run: set CHITRAVERSE_X_BEARER_TOKEN to use the official API.', flush=True)
        return

    def api_get(path):
        req = urllib.request.Request(API + path, headers={'Authorization': f'Bearer {token}', 'User-Agent': 'Chitraverse/0.1'})
        with urllib.request.urlopen(req, timeout=30) as response:
            raw = response.read(5_000_001)
            if len(raw) > 5_000_000:
                raise ValueError('X API page exceeded the 5 MB response cap')
            return json.loads(raw.decode('utf-8'))

    try:
        user_result = api_get('/users/by/username/' + HANDLE + '?user.fields=id,username,name,description,verified')
        user = user_result['data']
        if user.get('username', '').casefold() != HANDLE:
            raise ValueError('X API resolved a different account handle')
        write_json(root / 'catalog/x-account.json', {k: v for k, v in user.items() if k != 'description'} | {'checked_at': now()})
        token_page = None
        collected = 0
        page_count = 0
        while collected < limit and page_count < 40:
            params = {'max_results': min(100, max(5, limit - collected)),
                      'tweet.fields': 'created_at,lang,public_metrics,conversation_id,referenced_tweets,attachments',
                      'exclude': 'retweets'}
            if token_page:
                params['pagination_token'] = token_page
            page = api_get('/users/' + urllib.parse.quote(user['id']) + '/tweets?' + urllib.parse.urlencode(params))
            tweets = page.get('data', [])
            for tweet in tweets:
                tweet_id = tweet['id']
                url = f'https://x.com/{HANDLE}/status/{tweet_id}'
                text = tweet.get('text', '')
                text_path = root / 'private/tweets' / f'{tweet_id}.txt'
                text_path.parent.mkdir(parents=True, exist_ok=True)
                text_path.write_text(text + '\n', encoding='utf-8')
                record = {'url': url, 'tweet_id': tweet_id, 'author_id': user['id'], 'created_at': tweet.get('created_at'),
                          'lang': tweet.get('lang'), 'public_metrics': tweet.get('public_metrics'),
                          'conversation_id': tweet.get('conversation_id'), 'referenced_tweets': tweet.get('referenced_tweets', []),
                          'text_path': text_path.relative_to(root).as_posix(), 'text_sha256': digest(text),
                          'source': 'official_x_api_v2', 'retrieved_at': now()}
                upsert(root / 'catalog/tweets.jsonl', [record])
                collected += 1
                if collected >= limit:
                    break
            page_count += 1
            token_page = page.get('meta', {}).get('next_token')
            if not token_page or not tweets:
                break
        upsert(root / 'catalog/backlog.jsonl', [{'url': profile, 'kind': 'tweets', 'status': 'scan_complete_for_available_api_window',
               'detail': f'Collected {collected} public posts across {page_count} pages. X API timeline retention and pagination limits may exclude older posts; verify account archive for historical completeness.'}])
        print(f'X public posts collected: {collected} across {page_count} pages.', flush=True)
    except (urllib.error.HTTPError, urllib.error.URLError, KeyError, ValueError, json.JSONDecodeError) as exc:
        upsert(root / 'catalog/acquisition.jsonl', [{'url': profile, 'kind': 'x_timeline', 'status': 'failed',
               'checked_at': now(), 'error': str(exc)[:500]}])
        print(f'X timeline scan failed: {exc}', flush=True)
