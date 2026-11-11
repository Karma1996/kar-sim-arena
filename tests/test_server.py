import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

from arcade.server import create_server


class ServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dir = tempfile.TemporaryDirectory()
        cls.server = create_server("127.0.0.1", 0, str(Path(cls.dir.name) / "scores.json"))
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.server.server_address[1]}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.dir.cleanup()

    def test_health(self):
        with urllib.request.urlopen(f"{self.base}/health") as response:
            self.assertEqual(json.loads(response.read())["status"], "ok")

    def test_index_is_html(self):
        with urllib.request.urlopen(f"{self.base}/") as response:
            body = response.read().decode()
            self.assertIn("Arcade", body)

    def test_score_roundtrip(self):
        payload = json.dumps({"name": "karma", "score": 42}).encode()
        request = urllib.request.Request(
            f"{self.base}/api/score",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request) as response:
            self.assertEqual(response.status, 201)
        with urllib.request.urlopen(f"{self.base}/api/scores") as response:
            scores = json.loads(response.read())
        self.assertIn({"name": "karma", "score": 42}, scores)

    def test_bad_score_is_rejected(self):
        payload = json.dumps({"name": "", "score": -5}).encode()
        request = urllib.request.Request(
            f"{self.base}/api/score",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with self.assertRaises(urllib.error.HTTPError) as context:
            urllib.request.urlopen(request)
        self.assertEqual(context.exception.code, 400)

    def test_unknown_route_is_404(self):
        with self.assertRaises(urllib.error.HTTPError) as context:
            urllib.request.urlopen(f"{self.base}/nope")
        self.assertEqual(context.exception.code, 404)


if __name__ == "__main__":
    unittest.main()
