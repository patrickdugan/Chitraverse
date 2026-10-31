# Collection runbook

## Scope and sources

The official personal site `tarunchitra.com` is the first-party source for its Blog, Papers, and linked material. The scanner follows first-party links and any site sitemap it can access. The ArXiv Atom API is used for author-name discovery; papers are considered exact-name matches only when the source author list contains “Tarun Chitra”. Other links and citations remain separate from authored work.

Public podcast and interview pages are discovered through explicit source seeds, publisher indexes, the Apple episode directory, and podcast RSS feeds. A search result or passing mention stays a candidate until the publisher page supports guest participation. Video uploads, audio feed entries, and mirrors may point to the same underlying conversation.

The X account `@tarunchitra` is linked as an identity source from the personal site. Historical timeline collection uses X’s official API v2 only. The API bearer token must be passed as `CHITRAVERSE_X_BEARER_TOKEN` in the process environment. It is not written to disk. No unofficial mirror, login cookie, proxy, or access-control workaround is used. Without credentials the tweets command records the gap. API retention and endpoint access may still exclude older posts.

## Local content and reuse

Full texts, transcripts, ASR, and tweet text live under ignored `private/`. HTTP caches and search indexes live under ignored `.cache/`; transient recordings live under ignored `media/`. Committed catalogs retain source URLs, hashes, source metadata, and retrieval/identity status. Review applicable publisher and X terms before any redistribution. The original source’s rights remain in effect.

## Resume and verify

1. Inspect `catalog/provider-state.json`, `catalog/acquisition.jsonl`, `catalog/backlog.jsonl`, and `reports/coverage.json`.
2. Resume with the appropriate `chitraverse` command. Do not repeatedly retry a host during its recorded cooldown.
3. Review identity candidates; regenerate the report and local search index with `chitraverse report`.
4. Run `chitraverse validate` and `python -m unittest discover -s tests -v` after code changes.
5. Commit completed local work. Never push or open a PR unless the user explicitly asks.

No recurring schedule is installed. Exhaustive coverage is not claimed while source indexes, tweet history, or participation reviews remain incomplete.
