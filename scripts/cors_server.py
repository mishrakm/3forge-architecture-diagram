#!/usr/bin/env python3
"""Tiny static file server with permissive CORS headers for local dashboard viewing."""

from __future__ import annotations

import argparse
import http.server
import socketserver
from pathlib import Path


class CORSRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Serve static files and add CORS headers on all responses."""

    def end_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        super().end_headers()

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(204)
        self.end_headers()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a tiny static server with CORS enabled."
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Bind host (default: 0.0.0.0).",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Bind port (default: 8080).",
    )
    parser.add_argument(
        "--dir",
        default="docs",
        help="Directory to serve (default: docs).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    serve_dir = Path(args.dir).resolve()
    if not serve_dir.exists() or not serve_dir.is_dir():
        raise SystemExit(f"Directory not found: {serve_dir}")

    handler = lambda *h_args, **h_kwargs: CORSRequestHandler(  # noqa: E731
        *h_args,
        directory=str(serve_dir),
        **h_kwargs,
    )

    with socketserver.TCPServer((args.host, args.port), handler) as httpd:
        print(f"Serving {serve_dir} at http://{args.host}:{args.port}")
        print("CORS: Access-Control-Allow-Origin = *")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
