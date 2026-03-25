#!/usr/bin/env python3

from __future__ import annotations

import argparse
import os
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT / "docs"


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
        default=8000,
        help="Port to listen on. Default: 8000",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    os.chdir(DOCS_DIR)
    server = ThreadingHTTPServer(
        (args.host, args.port),
        SimpleHTTPRequestHandler,
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
