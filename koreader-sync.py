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

    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        print(f"DEBUG GET: {self.path}")
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
        content_length = int(self.headers.get('Content-Length', 0))
        body_str = self.rfile.read(content_length).decode()
        
        try:
            data = json.loads(body_str)
            doc_hash = data.get("document") # TU JE TEN 939ee5...
            
            with sqlite3.connect(DB_PATH) as conn:
                # 1. Uložíme pod pôvodnou cestou
                conn.execute("INSERT OR REPLACE INTO sync VALUES (?, ?)", (self.path, body_str))
                # 2. Uložíme pod cestou, ktorú bude pýtať MO (ten hash)
                if doc_hash:
                    full_path = f"/v1/syncs/progress/{doc_hash}"
                    conn.execute("INSERT OR REPLACE INTO sync VALUES (?, ?)", (full_path, body_str))
                    print(f"SAVED BOTH: {self.path} AND {full_path}")
        except Exception as e:
            print(f"ERROR: {e}")
            with sqlite3.connect(DB_PATH) as conn:
                conn.execute("INSERT OR REPLACE INTO sync VALUES (?, ?)", (self.path, body_str))

        self._send_json(json.loads(body_str) if body_str.startswith('{') else {"status":"ok"}, 201)

    def do_PATCH(self):
        self.do_PUT()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, PUT, PATCH, OPTIONS, HEAD")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 10000))
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()
