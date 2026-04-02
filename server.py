#!/usr/bin/env python3
"""
HDRnote 本地伺服器
執行方式: python server.py
本機訪問: http://localhost:8080
手機訪問: http://你的電腦IP:8080  (需在同一 WiFi)
"""

import json
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler

PATIENTS_FILE = 'patients.json'
PORT = 8080


class Handler(SimpleHTTPRequestHandler):

    def send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()

    def do_GET(self):
        if self.path == '/api/patients':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_cors_headers()
            self.end_headers()
            if os.path.exists(PATIENTS_FILE):
                with open(PATIENTS_FILE, 'r', encoding='utf-8') as f:
                    self.wfile.write(f.read().encode('utf-8'))
            else:
                self.wfile.write(b'null')
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == '/api/patients':
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            with open(PATIENTS_FILE, 'w', encoding='utf-8') as f:
                f.write(body.decode('utf-8'))
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(b'{"ok":true}')
        else:
            self.send_response(405)
            self.end_headers()

    def log_message(self, format, *args):
        print(f"[HDRnote] {format % args}")


if __name__ == '__main__':
    import socket
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)

    server = HTTPServer(('0.0.0.0', PORT), Handler)
    print(f"\n{'='*45}")
    print(f"  🏥  HDRnote 伺服器已啟動")
    print(f"{'='*45}")
    print(f"  💻  本機:   http://localhost:{PORT}")
    print(f"  📱  手機:   http://{local_ip}:{PORT}")
    print(f"  📂  資料:   {os.path.abspath(PATIENTS_FILE)}")
    print(f"  ⏹️   停止:   Ctrl+C")
    print(f"{'='*45}\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n伺服器已停止")
