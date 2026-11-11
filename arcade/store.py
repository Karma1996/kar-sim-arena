"""High-score persistence.

A JSON file on disk keeps the arena dependency-free. The store is intentionally
simple: the leaderboard *page* is a feature the squad still has to deliver.
"""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path


class StoreError(ValueError):
    pass


@dataclass(frozen=True)
class Entry:
    name: str
    score: int


class ScoreStore:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def entries(self) -> list[Entry]:
        if not self.path.exists():
            return []
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise StoreError(f"{self.path} is corrupt") from exc
        if not isinstance(raw, list):
            raise StoreError("score file must contain a list")
        return [
            Entry(str(item["name"]), int(item["score"]))
            for item in raw
            if isinstance(item, dict) and "name" in item and "score" in item
        ]

    def add(self, name: str, score: int) -> Entry:
        name = name.strip()
        if not 1 <= len(name) <= 24:
            raise StoreError("name must be 1..24 characters")
        if not isinstance(score, int) or not 0 <= score <= 100000:
            raise StoreError("score must be a non-negative integer")
        items = self.entries() + [Entry(name, score)]
        self._write(items)
        return Entry(name, score)

    def top(self, limit: int = 10) -> list[Entry]:
        if limit <= 0:
            return []
        return sorted(self.entries(), key=lambda item: (-item.score, item.name))[:limit]

    def _write(self, items: list[Entry]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        handle, name = tempfile.mkstemp(dir=self.path.parent, prefix=".scores-")
        with os.fdopen(handle, "w", encoding="utf-8") as stream:
            json.dump([asdict(item) for item in items], stream, ensure_ascii=False)
        os.replace(name, self.path)
