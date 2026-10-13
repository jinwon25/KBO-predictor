"""정적 운영 화면 기록에 실행 코드와 외부 연결이 섞이지 않는지 검증합니다."""
import re
import struct
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VIEWS = ('prediction', 'schedule', 'submission', 'accuracy', 'statistics', 'mobile')


class ParsedHTML(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.elements = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        self.elements.append((tag, dict(attrs)))


class ShowcaseTests(unittest.TestCase):
    def test_snapshots_are_static_and_marked(self):
        for name in VIEWS:
            with self.subTest(view=name):
                text = (ROOT / 'docs/showcase' / (name + '.html')).read_text(encoding='utf8')
                parsed = ParsedHTML(text)
                root = next(attrs for tag, attrs in parsed.elements if tag == 'html')
                self.assertEqual(root.get('data-capture-ready'), 'true')
                self.assertEqual(root.get('data-synthetic-data'), 'true')
                self.assertEqual(root.get('data-render-errors'), '[]')
                self.assertIn('독립 합성 데이터', text)
                self.assertIn('실제 경기·제출 성적 아님', text)
                for tag, attrs in parsed.elements:
                    self.assertNotIn(tag, ('script', 'iframe', 'object', 'embed', 'base', 'link', 'form'))
                    self.assertFalse(any(key.lower().startswith('on') for key in attrs))
                    self.assertFalse({'action', 'formaction', 'ping', 'srcset'} & attrs.keys())
                    if tag in ('button', 'input', 'select', 'textarea'):
                        self.assertIn('disabled', attrs)
                    if tag == 'img':
                        self.assertTrue(attrs.get('src', '').startswith('data:image/'))
                    if 'href' in attrs:
                        self.assertEqual(attrs['href'], 'index.html')
                policy = next(attrs.get('content', '') for tag, attrs in parsed.elements
                              if tag == 'meta' and attrs.get('http-equiv', '').lower() == 'content-security-policy')
                for clause in ("script-src 'none'", "connect-src 'none'", "form-action 'none'", "base-uri 'none'"):
                    self.assertIn(clause, policy)
                self.assertNotRegex(text, r'/api/|/static/|https?://(?!www\.w3\.org/2000/svg)')
                for target in re.findall(r'url\(([^)]*)\)', text, flags=re.I):
                    self.assertTrue(target.strip(" '\"").startswith(('#', 'data:')), target)

    def test_gallery_has_local_images_and_views(self):
        text = (ROOT / 'docs/showcase/index.html').read_text(encoding='utf8')
        parsed = ParsedHTML(text)
        links = [attrs.get('href') for tag, attrs in parsed.elements if tag == 'a']
        for name in VIEWS:
            self.assertIn(name + '.html', links)
        for tag, attrs in parsed.elements:
            self.assertNotIn(tag, ('script', 'iframe', 'form'))
            if tag == 'img':
                self.assertTrue(attrs.get('alt'))
                self.assertTrue((ROOT / 'docs/showcase' / attrs['src']).is_file())

    def test_png_dimensions_match_the_documented_viewports(self):
        for name in VIEWS:
            with self.subTest(view=name):
                png = (ROOT / 'docs/images' / ('operating-ui-preview-' + name + '.png')).read_bytes()
                self.assertEqual(png[:8], b'\x89PNG\r\n\x1a\n')
                expected = (390, 920) if name == 'mobile' else (1440, 1100)
                self.assertEqual(struct.unpack('>II', png[16:24]), expected)


if __name__ == '__main__':
    unittest.main()
