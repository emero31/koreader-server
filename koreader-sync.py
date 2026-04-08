import os, sqlite3, json
from http.server import BaseHTTPRequestHandler, HTTPServer

DB_PATH = "koreader.db"

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS sync (key TEXT PRIMARY KEY, val TEXT)")

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Odpovieme na /v1/auth aj na čokoľvek iné pre auth
        if "auth" in self.path:
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"username":"emero31","token":"ok"}).encode())
        else:
            # Tu hľadáme uložený priebeh
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
        # Toto spracuje ukladanie priebehu aj PAZ
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length).decode()
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("INSERT OR REPLACE INTO sync VALUES (?, ?)", (self.path, body))
        self.send_response(201)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"status":"created"}).encode())

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 10000))
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()
