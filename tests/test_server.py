import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from demo.server import Handler


class ServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = f'http://127.0.0.1:{cls.server.server_port}'

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def test_assets_and_api(self):
        for path in ['/', '/style.css', '/app.js', '/api/demo']:
            with urlopen(self.url + path, timeout=3) as response:
                self.assertEqual(response.status, 200)
                self.assertEqual(response.headers['X-Content-Type-Options'], 'nosniff')
                self.assertTrue(response.read())
        with urlopen(self.url + '/api/demo', timeout=3) as response:
            self.assertTrue(json.load(response)['synthetic'])

    def test_write_requests_rejected(self):
        for method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            with self.subTest(method=method), self.assertRaises(HTTPError) as raised:
                urlopen(Request(self.url + '/api/demo', data=b'{}', method=method), timeout=3)
            self.assertEqual(raised.exception.code, 405)

    def test_only_allowlisted_paths_are_served(self):
        for path in ['/README.md', '/../demo/server.py', '/.env', '/static/nope', '/api/status']:
            with self.subTest(path=path), self.assertRaises(HTTPError) as raised:
                urlopen(self.url + path, timeout=3)
            self.assertEqual(raised.exception.code, 404)
