from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            with open("feed.xml", "r", encoding="utf-8") as f:
                data = f.read()

            self.send_response(200)
            self.send_header("Content-type", "application/rss+xml")
            self.end_headers()
            self.wfile.write(data.encode("utf-8"))

        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode())
