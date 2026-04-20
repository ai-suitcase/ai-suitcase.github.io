#!/usr/bin/env python3

from __future__ import annotations

import argparse
import posixpath
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT / "docs"
DOCS_ALIAS = "/docs"


def normalize_request_path(path: str) -> str:
    normalized = posixpath.normpath(urlsplit(path).path)
    if normalized in {".", DOCS_ALIAS}:
        return "/"
    if normalized.startswith(f"{DOCS_ALIAS}/"):
        return normalized[len(DOCS_ALIAS) :] or "/"
    return normalized if normalized.startswith("/") else f"/{normalized}"


class DocsHTTPRequestHandler(SimpleHTTPRequestHandler):
    def translate_path(self, path: str) -> str:
        return super().translate_path(normalize_request_path(path))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Serve the generated docs/ directory locally."
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host interface to bind to. Default: 127.0.0.1",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8002,
        help="Port to listen on. Default: 8002",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    handler = partial(DocsHTTPRequestHandler, directory=str(DOCS_DIR))
    server = ThreadingHTTPServer(
        (args.host, args.port),
        handler,
    )
    print(f"Serving {DOCS_DIR} at http://{args.host}:{args.port}/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
