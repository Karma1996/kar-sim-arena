import tempfile
import unittest
from pathlib import Path

from arcade.store import Entry, ScoreStore, StoreError


class StoreTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = Path(self.dir.name) / "scores.json"
        self.store = ScoreStore(self.path)

    def tearDown(self):
        self.dir.cleanup()

    def test_empty_file_reads_as_empty(self):
        self.assertEqual(self.store.entries(), [])

    def test_add_persists(self):
        self.store.add("karma", 30)
        self.assertEqual(ScoreStore(self.path).entries(), [Entry("karma", 30)])

    def test_top_is_sorted_and_limited(self):
        for name, score in [("a", 10), ("b", 50), ("c", 30)]:
            self.store.add(name, score)
        self.assertEqual([e.name for e in self.store.top(2)], ["b", "c"])

    def test_validation(self):
        with self.assertRaises(StoreError):
            self.store.add("", 10)
        with self.assertRaises(StoreError):
            self.store.add("x" * 25, 10)
        with self.assertRaises(StoreError):
            self.store.add("karma", -1)

    def test_corrupt_file_is_reported(self):
        self.path.write_text("{not json", encoding="utf-8")
        with self.assertRaises(StoreError):
            self.store.entries()


if __name__ == "__main__":
    unittest.main()
