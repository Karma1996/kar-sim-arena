"""HTTP surface for the arena product.

Run: ``python3 -m arcade.server --port 8000``. The static page plays the game;
scores are persisted through ``POST /api/score``. There is no leaderboard page
and no login yet — those are the features the evaluation cases ask for.
"""

from __future__ import annotations

import argparse
import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from .store import ScoreStore, StoreError

STATIC = Path(__file__).resolve().parent.parent / "static"


def make_handler(store: ScoreStore):
    class Handler(BaseHTTPRequestHandler):
        server_version = "Arcade/0.1"

        def do_GET(self) -> None:  # noqa: N802
            path = urlparse(self.path).path
            if path == "/api/scores":
                self._json([entry.__dict__ for entry in store.entries()])
                return
            if path == "/health":
                self._json({"status": "ok"})
                return
            if path in {"/", "/index.html"}:
                self._file(STATIC / "index.html", "text/html; charset=utf-8")
                return
            if path.startswith("/static/"):
                target = (STATIC / path.removeprefix("/static/")).resolve()
                if not str(target).startswith(str(STATIC.resolve())) or not target.is_file():
                    self._json({"error": "not found"}, HTTPStatus.NOT_FOUND)
                    return
                self._file(target, "text/javascript" if target.suffix == ".js" else "text/css")
                return
            self._json({"error": "not found"}, HTTPStatus.NOT_FOUND)

        def do_POST(self) -> None:  # noqa: N802
            if urlparse(self.path).path != "/api/score":
                self._json({"error": "not found"}, HTTPStatus.NOT_FOUND)
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                payload = json.loads(self.rfile.read(length) or b"{}")
                entry = store.add(str(payload.get("name", "")), int(payload.get("score", 0)))
            except (ValueError, StoreError, json.JSONDecodeError) as exc:
                self._json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
                return
            self._json({"saved": entry.__dict__}, HTTPStatus.CREATED)

        def _json(self, payload, status: HTTPStatus = HTTPStatus.OK) -> None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _file(self, path: Path, content_type: str) -> None:
            body = path.read_bytes()
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args) -> None:  # keep test output quiet
            return

    return Handler


def create_server(host: str = "127.0.0.1", port: int = 8000, scores: str = "scores.json"):
    return ThreadingHTTPServer((host, port), make_handler(ScoreStore(scores)))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the arcade server")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--scores", default="scores.json")
    args = parser.parse_args(argv)
    server = create_server(args.host, args.port, args.scores)
    print(f"arcade listening on http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
