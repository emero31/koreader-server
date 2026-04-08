import os, sqlite3, json

DB_PATH = "koreader.db"

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS sync (key TEXT PRIMARY KEY, val TEXT)")

class Handler(BaseHTTPRequestHandler):
    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("x-auth-token", "ok-token")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_GET(self):
        # Ak KOReader pýta login
        if "auth" in self.path:
            return self._send_json({"username":"emero31","token":"ok-token"})
        
        # Hľadáme dáta (či už progress alebo metadata s PAZ)
        with sqlite3.connect(DB_PATH) as conn:
            res = conn.execute("SELECT val FROM sync WHERE key=?", (self.path,)).fetchone()
            if res:
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(res[0].encode())
            else:
                self.send_response(404)
                self.end_headers()

    def do_PUT(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body_str = self.rfile.read(content_length).decode()
        
        # Ukladáme VŠETKO pod cestou, ktorú KOReader poslal
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("INSERT OR REPLACE INTO sync VALUES (?, ?)", (self.path, body_str))
        
        # Ak poslal progress, KOReader-Go vyžaduje vrátiť ten istý objekt
        try:
            resp = json.loads(body_str)
        except:
            resp = {"status":"ok"}
            
        self._send_json(resp, 201)

    # Dôležité: KOSync-Go používa PATCH pre aktualizáciu poznámok!
    def do_PATCH(self):
        self.do_PUT()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, PUT, PATCH, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()

from http.server import BaseHTTPRequestHandler, HTTPServer
if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 10000))
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()
