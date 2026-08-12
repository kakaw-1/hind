#!/usr/bin/env python3
"""Hindsight API Bearer-auth reverse proxy (Space A front door).
Hindsight OSS API (0.8.x) has NO built-in auth; this proxy sits on :7860 and
requires `Authorization: Bearer <HINDSIGHT_AUTH_TOKEN>` for everything except
/health and /metrics (kept open for HF Spaces health-check), then forwards to
the real API on 127.0.0.1:8888.
"""
import http.client
import http.server
import os
import sys

BACKEND_HOST = "127.0.0.1"
BACKEND_PORT = int(os.environ.get("HINDSIGHT_API_PORT", "8888"))
TOKEN = os.environ.get("HINDSIGHT_AUTH_TOKEN", "")
OPEN_PREFIXES = ("/health", "/metrics")
PORT = 7860


class ProxyHandler(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _handle(self):
        # Auth gate (except health/metrics for HF health-check)
        if not self.path.startswith(OPEN_PREFIXES):
            auth = self.headers.get("Authorization", "")
            if auth != f"Bearer {TOKEN}":
                self.send_response(401)
                self.send_header("Content-Length", "0")
                self.end_headers()
                return

        # Read body if present
        body = None
        if self.headers.get("Content-Length"):
            try:
                body = self.rfile.read(int(self.headers["Content-Length"]))
            except Exception:
                body = None

        # Forward
        try:
            conn = http.client.HTTPConnection(BACKEND_HOST, BACKEND_PORT, timeout=300)
            fwd_headers = {
                k: v
                for k, v in self.headers.items()
                if k.lower() not in ("host", "connection", "content-length", "accept-encoding")
            }
            conn.request(self.command, self.path, body=body, headers=fwd_headers)
            resp = conn.getresponse()
            data = resp.read()
            self.send_response(resp.status)
            for k, v in resp.getheaders():
                if k.lower() in ("content-length", "content-type", "location", "set-cookie"):
                    self.send_header(k, v)
            self.end_headers()
            if data:
                self.wfile.write(data)
            conn.close()
        except Exception as e:
            self.send_response(502)
            self.send_header("Content-Length", "0")
            self.end_headers()
            sys.stderr.write(f"[auth_proxy] {e}\n")

    do_GET = do_POST = do_PUT = do_DELETE = do_PATCH = do_OPTIONS = _handle

    def log_message(self, *args):  # silence
        pass


if __name__ == "__main__":
    http.server.ThreadingHTTPServer(("0.0.0.0", PORT), ProxyHandler).serve_forever()
