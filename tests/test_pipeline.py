import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from chitraverse.core import canonical, article, links, upsert, rows
from chitraverse.tweets import collect_tweets
from bs4 import BeautifulSoup


class ChitraverseTests(unittest.TestCase):
    def test_canonical_preserves_identity_and_removes_tracking(self):
        self.assertEqual(canonical('https://tarunchitra.com/blog/?utm_source=x'), 'https://tarunchitra.com/blog')
        self.assertEqual(canonical('https://x.com/tarunchitra/status/1234567890123456789?ref_src=twsrc'), 'https://x.com/tarunchitra/status/1234567890123456789')

    def test_canonical_normalizes_video_ids(self):
        self.assertEqual(canonical('https://youtu.be/abcdefghijk?t=15'), 'https://www.youtube.com/watch?v=abcdefghijk')

    def test_article_extracts_main_content(self):
        soup = BeautifulSoup('<nav>skip</nav><main><h1>Essay</h1><p>Keep this.</p><script>skip</script></main>', 'html.parser')
        self.assertIn('Keep this.', article(soup))
        self.assertNotIn('skip', article(soup))

    def test_links_are_canonicalized(self):
        soup = BeautifulSoup('<a href="/papers/a.pdf">Paper</a>', 'html.parser')
        self.assertIn('https://tarunchitra.com/papers/a.pdf', links(soup, 'https://tarunchitra.com/'))

    def test_upsert_merges_by_url(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as tmp:
            path = Path(tmp) / 'rows.jsonl'
            upsert(path, [{'url': 'https://example.com/a', 'title': 'A'}])
            upsert(path, [{'url': 'https://example.com/a', 'status': 'stored'}])
            self.assertEqual(rows(path), [{'status': 'stored', 'title': 'A', 'url': 'https://example.com/a'}])

    def test_tweet_collector_records_gap_without_credentials(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as tmp, patch.dict(os.environ, {}, clear=True):
            root = Path(tmp)
            (root / 'catalog').mkdir()
            (root / 'config').mkdir()
            (root / 'config/tweet-seeds.json').write_text('[]', encoding='utf8')
            collect_tweets(root, fetch=None)
            backlog = rows(root / 'catalog/backlog.jsonl')
            self.assertEqual(backlog[0]['status'], 'credentials_required')
            self.assertFalse((root / 'private').exists())


if __name__ == '__main__':
    unittest.main()
