import os, sqlite3, json
from http.server import BaseHTTPRequestHandler, HTTPServer

DB_PATH = "koreader.db"

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS sync (key TEXT PRIMARY KEY, val TEXT)")

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Odpoveď pre prihlásenie
        if "auth" in self.path:
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"username":"emero31","token":"ok"}).encode())
        else:
            with sqlite3.connect(DB_PATH) as conn:
                res = conn.execute("SELECT val FROM sync WHERE key=?", (self.path,)).fetchone()
                if res:
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    # KOReader miluje ETagy
                    self.send_header("ETag", "12345")
                    self.end_headers()
                    self.wfile.write(res[0].encode())
                else:
                    self.send_response(404)
                    self.end_headers()

    def do_PUT(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length).decode()
        
        # Uložíme všetko, čo príde
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("INSERT OR REPLACE INTO sync VALUES (?, ?)", (self.path, body))
        
        # Toto je tá kľúčová odpoveď, ktorú KOReader vyžaduje
        self.send_response(201)
        self.send_header("Content-Type", "application/json")
        self.send_header("ETag", "12345")
        self.end_headers()
        self.wfile.write(json.dumps({"status":"created"}).encode())

    # KOReader niekedy posiela predbežný dotaz (Preflight)
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Methods", "GET, PUT, OPTIONS")
        self.end_headers()

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 10000))
    print(f"Server beží na porte {port}")
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()
