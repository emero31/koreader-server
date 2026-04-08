import os, sqlite3, json, time
from http.server import BaseHTTPRequestHandler, HTTPServer

DB_PATH = "koreader.db"

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS sync (key TEXT PRIMARY KEY, val TEXT)")

class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Toto nám vypíše cestu do logov na Renderi
        print(f"DEBUG: {self.command} {self.path}")

    def do_GET(self):
        if "auth" in self.path:
            self._send_json({"username":"emero31","token":"ok-token"})
        else:
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
        
        # Uložíme dáta
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("INSERT OR REPLACE INTO sync VALUES (?, ?)", (self.path, body_str))
        
        # PRÍPRAVA ODPOVEDE, KTORÚ PLUGIN MILUJE
        try:
            data = json.loads(body_str)
            # Pridáme timestamp, ak tam nie je
            if "timestamp" not in data:
                data["timestamp"] = int(time.time())
        except:
            data = {"status": "created"}

        self.send_response(201)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, PUT, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()

    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 10000))
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()
