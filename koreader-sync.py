import os, sqlite3, json
from http.server import BaseHTTPRequestHandler, HTTPServer

DB_PATH = "koreader.db"

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS sync (key TEXT PRIMARY KEY, val TEXT)")

class Handler(BaseHTTPRequestHandler):
    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("x-auth-token", "ok-token") # KOReader toto vyžaduje
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_GET(self):
        # Ak sa pýta na prihlásenie (auth)
        if "auth" in self.path:
            self._send_json({"username":"emero31","token":"ok-token"})
        else:
            # Hľadáme dáta pre akúkoľvek cestu, ktorú KOReader pošle
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
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length).decode()
        # Uložíme to pod kľúčom, ktorý poslal KOReader (napr. /users/emero31/koreaderfs/...)
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("INSERT OR REPLACE INTO sync VALUES (?, ?)", (self.path, body))
        self._send_json({"status":"created"}, 201)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Methods", "GET, PUT, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "x-auth-token, Content-Type")
        self.end_headers()

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 10000))
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()
