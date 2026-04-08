import os, sqlite3, json
from http.server import BaseHTTPRequestHandler, HTTPServer

# Cesta k databáze v koreňovom priečinku Renderu
DB_PATH = "koreader.db"

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS sync (key TEXT PRIMARY KEY, val TEXT)")

class Handler(BaseHTTPRequestHandler):
    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("x-auth-token", "ok-token")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_HEAD(self):
        """Odpoveď pre Render Health Check, aby svietilo LIVE."""
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        """Načítanie dát pre mobil (MO) aj prihlásenie."""
        print(f"DEBUG GET: {self.path}")
        if "auth" in self.path:
            return self._send_json({"username":"emero31","token":"ok-token"})
        
        with sqlite3.connect(DB_PATH) as conn:
            res = conn.execute("SELECT val FROM sync WHERE key=?", (self.path,)).fetchone()
            if res:
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(res[0].encode())
            else:
                self._send_json({"error": "not found"}, 404)

    def do_PUT(self):
        """Ukladanie dát z Booxu (GO)."""
        print(f"DEBUG PUT: {self.path}")
        content_length = int(self.headers.get('Content-Length', 0))
        body_str = self.rfile.read(content_length).decode()
        
        # TENTO RIADOK NÁM POVIE, ČI BOOX POSIELA POZNÁMKY:
        print(f"BODY CONTENT: {body_str[:300]}...") 

        try:
            data = json.loads(body_str)
            doc_hash = data.get("document")
            
            with sqlite3.connect(DB_PATH) as conn:
                # Uložíme pod pôvodnou cestou (/v1/syncs/progress)
                conn.execute("INSERT OR REPLACE INTO sync VALUES (?, ?)", (self.path, body_str))
                # Uložíme aj pod cestou s hash-om, ktorú hľadá mobil
                if doc_hash:
                    full_path = f"/v1/syncs/progress/{doc_hash}"
                    conn.execute("INSERT OR REPLACE INTO sync VALUES (?, ?)", (full_path, body_str))
                    print(f"SUCCESS: Saved to {full_path}")
        except Exception as e:
            print(f"JSON ERROR: {e}")
            with sqlite3.connect(DB_PATH) as conn:
                conn.execute("INSERT OR REPLACE INTO sync VALUES (?, ?)", (self.path, body_str))

        self._send_json(json.loads(body_str) if body_str.startswith('{') else {"status":"ok"}, 201)

    def do_PATCH(self):
        """Podpora pre aktualizáciu poznámok."""
        print(f"DEBUG PATCH: {self.path}")
        self.do_PUT()

    def do_OPTIONS(self):
        """CORS podpora pre istotu."""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, PUT, PATCH, OPTIONS, HEAD")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 10000))
    print(f"Emero Sync Server štartuje na porte {port}...")
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()
