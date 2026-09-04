"""Kleiner statischer Test-Server mit korrekten MIME-Types fuer pygbag-Builds.

Nur fuer lokales Testen des statischen Deployments (simuliert GitHub Pages,
das .wasm als application/wasm ausliefert). KEIN Proxy fuer /cdn/ -> so sehen
wir, ob die pygbag-Runtime das pygame-Wheel vom echten CDN oder vom Host laedt.
"""
import http.server
import socketserver
import sys

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8002
DIRECTORY = sys.argv[2] if len(sys.argv) > 2 else "build/web"


class Handler(http.server.SimpleHTTPRequestHandler):
    extensions_map = {
        **http.server.SimpleHTTPRequestHandler.extensions_map,
        ".wasm": "application/wasm",
        ".js": "text/javascript",
        ".mjs": "text/javascript",
        ".data": "application/octet-stream",
        ".whl": "application/octet-stream",
        ".apk": "application/octet-stream",
        ".gz": "application/gzip",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)


with socketserver.TCPServer(("127.0.0.1", PORT), Handler) as httpd:
    print(f"Static server on http://127.0.0.1:{PORT}/ serving {DIRECTORY}")
    httpd.serve_forever()
