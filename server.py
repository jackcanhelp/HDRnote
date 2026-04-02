#!/usr/bin/env python3
"""
HDRnote 本地伺服器
啟動方式: 執行 start.bat（自動帶密碼 + Tunnel）
直接啟動: python server.py（需先手動 set HDR_PASSWORD=...）
"""

import json
import os
import socket
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

PASSWORD     = os.getenv('HDR_PASSWORD', '')
PATIENTS_FILE = Path('patients.json')
PORT         = 8080


class Handler(SimpleHTTPRequestHandler):

    # ── 驗證密碼 ─────────────────────────────────────────────
    def check_auth(self):
        if not PASSWORD:
            print('[HDRnote] ⚠️  HDR_PASSWORD 未設定，請透過 start.bat 啟動')
            return False
        return self.headers.get('X-Password', '') == PASSWORD

    # ── 共用回應工具 ──────────────────────────────────────────
    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self._cors()
        self.end_headers()
        self.wfile.write(body)

    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-Password')

    # ── OPTIONS preflight（Cloudflare Tunnel 需要）────────────
    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    # ── GET ──────────────────────────────────────────────────
    def do_GET(self):
        # 健康檢查（不需密碼）
        if self.path == '/api/ping':
            self.send_json({'ok': True})

        # 取得病人資料
        elif self.path == '/api/patients':
            if not self.check_auth():
                self.send_json({'error': 'Unauthorized'}, 401)
                return
            if PATIENTS_FILE.exists():
                data = json.loads(PATIENTS_FILE.read_text('utf-8'))
                self.send_json(data)
            else:
                self.send_json(None)

        # 其他 → 靜態檔案（index.html 等）
        else:
            super().do_GET()

    # ── POST ─────────────────────────────────────────────────
    def do_POST(self):
        # 儲存病人資料
        if self.path == '/api/patients':
            if not self.check_auth():
                self.send_json({'error': 'Unauthorized'}, 401)
                return
            length = int(self.headers.get('Content-Length', 0))
            body   = self.rfile.read(length)
            # 驗證是合法 JSON 才寫入
            try:
                json.loads(body)
            except json.JSONDecodeError:
                self.send_json({'error': 'Invalid JSON'}, 400)
                return
            PATIENTS_FILE.write_bytes(body)
            print(f'[HDRnote] 💾 patients.json 已更新 ({len(body)} bytes)')
            self.send_json({'ok': True})
        else:
            self.send_response(405)
            self.end_headers()

    def log_message(self, format, *args):
        print(f'[HDRnote] {format % args}')


if __name__ == '__main__':
    if not PASSWORD:
        print('⚠️  警告: HDR_PASSWORD 未設定，請透過 start.bat 啟動')

    try:
        local_ip = socket.gethostbyname(socket.gethostname())
    except Exception:
        local_ip = '127.0.0.1'

    server = HTTPServer(('0.0.0.0', PORT), Handler)
    print(f'\n{"="*50}')
    print(f'  🏥  HDRnote 伺服器已啟動')
    print(f'{"="*50}')
    print(f'  💻  本機:   http://localhost:{PORT}')
    print(f'  📱  區網:   http://{local_ip}:{PORT}')
    print(f'  📂  資料:   {PATIENTS_FILE.resolve()}')
    print(f'  🔑  密碼:   {"已設定" if PASSWORD else "❌ 未設定"}')
    print(f'  ⏹️   停止:   Ctrl+C')
    print(f'{"="*50}\n')

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n伺服器已停止')
