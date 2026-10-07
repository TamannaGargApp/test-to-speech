"""
Local frontend server for development without Docker.

Serves the frontend/ folder and forwards /api/* requests to the FastAPI
backend, the same way nginx.conf does in Docker.

Usage (start the backend first):
    python dev_server.py            # http://localhost:3000
    python dev_server.py 5500       # custom port
"""

import os
import sys
import urllib.error
import urllib.request
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

BACKEND = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend")

# Headers that must not be copied between the two connections
HOP_HEADERS = {"connection", "keep-alive", "transfer-encoding", "host", "content-length"}


class DevHandler(SimpleHTTPRequestHandler):

    def _proxy(self):
        url = BACKEND + self.path[len("/api"):]
        length = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(length) if length else None
        headers = {k: v for k, v in self.headers.items() if k.lower() not in HOP_HEADERS}
        req = urllib.request.Request(url, data=body, headers=headers, method=self.command)

        try:
            resp = urllib.request.urlopen(req)
        except urllib.error.HTTPError as err:
            resp = err
        except urllib.error.URLError:
            try:
                self.send_error(502, f"Backend not reachable at {BACKEND}. Is uvicorn running?")
            except ConnectionError:
                pass  # browser already closed the connection
            return

        data = resp.read()
        self.send_response(resp.status if hasattr(resp, "status") else resp.code)
        for k, v in resp.headers.items():
            if k.lower() not in HOP_HEADERS:
                self.send_header(k, v)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _handle(self, fallback):
        if self.path.startswith("/api/"):
            self._proxy()
        else:
            fallback()

    def do_GET(self):
        self._handle(super().do_GET)

    def do_HEAD(self):
        self._handle(super().do_HEAD)

    def do_POST(self):
        self._handle(lambda: self.send_error(405))

    def do_PUT(self):
        self._handle(lambda: self.send_error(405))

    def do_DELETE(self):
        self._handle(lambda: self.send_error(405))


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
    handler = partial(DevHandler, directory=FRONTEND_DIR)
    print(f"Frontend: http://localhost:{port}  (API -> {BACKEND})")
    ThreadingHTTPServer(("", port), handler).serve_forever()
