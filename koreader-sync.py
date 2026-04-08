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
        self.send_header("x-auth-token", "ok-token")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_GET(self):
        print(f"DEBUG GET: {self.path}")
        if "auth" in self.path:
            self._send_json({"username":"emero31","token":"ok-token"})
        else:
            with sqlite3.connect(DB_PATH) as conn:
                # Skúsime nájsť dáta pre presnú cestu (hash knihy)
                res = conn.execute("SELECT val FROM sync WHERE key=?", (self.path,)).fetchone()
                if not res:
                    # Ak nenájde s konkrétnym hashom, skúsi všeobecný (fallback)
                    res = conn.execute("SELECT val FROM sync WHERE key='/v1/syncs/progress'").fetchone()
                
                if res:
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(res[0].encode())
                else:
                    self.send_response(404)
                    self.end_headers()

    def do_PUT(self):
        print(f"DEBUG PUT: {self.path}")
        content_length = int(self.headers.get('Content-Length', 0))
        body_str = self.rfile.read(content_length).decode()
        
        try:
            data = json.loads(body_str)
            # KLÚČOVÝ TRIK: Ak v dátach poslal hash dokumentu, uložíme to pod ním
            doc_hash = data.get("document")
            if doc_hash:
                # Vytvoríme cestu, ktorú bude mobil neskôr hľadať cez GET
                storage_path = f"/v1/syncs/progress/{doc_hash}"
                with sqlite3.connect(DB_PATH) as conn:
                    conn.execute("INSERT OR REPLACE INTO sync VALUES (?, ?)", (storage_path, body_str))
        except:
            pass

        # Uložíme aj pod pôvodnou cestou pre istotu
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("INSERT OR REPLACE INTO sync VALUES (?, ?)", (self.path, body_str))
        
        self._send_json(json.loads(body_str) if 'data' in locals() else {"status":"ok"}, 201)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, PUT, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 10000))
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()
