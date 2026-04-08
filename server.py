from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request
import json
import os

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'
        elif self.path == '/download':
            self.send_response(200)
            self.send_header('Content-Type', 'application/octet-stream')
            self.send_header('Content-Disposition', 'attachment; filename="trading_bot.py"')
            self.end_headers()
            # Create a dummy bot file (replace with your real .py)
            bot_code = '''#!/usr/bin/env python3
print("Thank you for purchasing from Koreruss!")
print("This is your AI trading bot. Replace with your actual code.")
'''
            self.wfile.write(bot_code.encode())
            return
        try:
            with open('.' + self.path, 'rb') as f:
                self.send_response(200)
                if self.path.endswith('.html'):
                    self.send_header('Content-type', 'text/html')
                else:
                    self.send_header('Content-type', 'application/octet-stream')
                self.end_headers()
                self.wfile.write(f.read())
        except:
            self.send_error(404)

    def do_POST(self):
        if self.path == '/analyze':
            length = int(self.headers['Content-Length'])
            body = self.rfile.read(length)
            data = json.loads(body)
            req = urllib.request.Request(
                'http://localhost:11434/api/generate',
                data=json.dumps({
                    "model": "moondream",
                    "prompt": "Describe this low-quality image briefly",
                    "images": [data['image']],
                    "stream": False
                }).encode(),
                method='POST'
            )
            req.add_header('Content-Type', 'application/json')
            with urllib.request.urlopen(req) as resp:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(resp.read())
        else:
            self.send_error(404)

print("✅ Server with download endpoint running on http://localhost:8080")
HTTPServer(('0.0.0.0', 8080), Handler).serve_forever()
