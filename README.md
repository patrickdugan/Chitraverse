# Chitraverse

A local, resumable source corpus for Tarun Chitra’s public writing, research papers, podcast and interview appearances, and public X posts. Chitraverse adapts the source provenance, transcript handling, and local search patterns developed for Levinverse and Goodfireverse.

## Start here

- [Coverage report](reports/coverage.md) summarizes what has been collected and what remains incomplete.
- `catalog/` stores source URLs, dates, authorship/participation evidence, transcript provenance, retrieval results, and review queues.
- `private/` holds full research copies and transcripts locally. It is ignored by Git.
- `.cache/search.sqlite3` is a rebuildable full-text index and is also ignored.

## Collect and resume

```powershell
python -m pip install -e ".[media]"
chitraverse discover
chitraverse publications
chitraverse papers
chitraverse media
chitraverse feeds
chitraverse captions
chitraverse tweets
chitraverse report
chitraverse validate
```

The collectors resume from catalogs and HTTP cache files. Failed requests remain in `catalog/acquisition.jsonl`; provider restrictions are respected. A failed caption request does not establish that captions are absent. Full publisher text, recordings and tweets are not committed.

### X / tweets

`chitraverse tweets` uses X’s official API v2 and needs `CHITRAVERSE_X_BEARER_TOKEN` in the process environment. The token is never saved. Without it, the scanner records the access gap and does not use unofficial mirrors or login workarounds. X API timeline retention can restrict older history, so even a successful scan is not described as exhaustive. Tweet text is stored only under ignored `private/tweets/`; the committed catalog contains URLs and metadata.

## Search

```powershell
chitraverse search --query 'market design' --limit 10
```

Search output includes source URL, local path, and matching passage. Publisher-provided transcripts keep their labels; ASR is identified as unverified and no speakers are invented. Source links and paper citations do not by themselves establish authorship.

## Coverage

The personal site is scanned from its linked pages and sitemap. ArXiv search results are checked against the exact author name; citations and coauthor candidates are kept separate. Interview/podcast identity is tied to publisher evidence. The appearance catalog distinguishes source URLs from underlying events. Full copyrighted material stays local and ignored unless a redistribution license is established.

No recurring task, remote publication, push, or PR workflow is configured by the collector.
