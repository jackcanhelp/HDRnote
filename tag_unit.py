"""
把現有病患標記所屬單位。
- 沒有 unit 欄位的正式病患 → unit: '國際桃庚'
- bed === '示範' 的虛擬病患 → 不動
執行完後可直接匯入大興鑫庚名單（import_daxing.py）
"""
import json, urllib.request, ssl, re
from pathlib import Path

SECRETS = Path(__file__).parent / 'secrets.bat'
pw = ''
if SECRETS.exists():
    m = re.search(r'set\s+HDR_PASSWORD\s*=\s*(\S+)', SECRETS.read_text(), re.IGNORECASE)
    if m: pw = m.group(1)

ctx = ssl.create_default_context()

# 下載現有資料
req = urllib.request.Request('https://hdr-note.vercel.app/api/patients',
    headers={'X-Password': pw}, method='GET')
patients = json.loads(urllib.request.urlopen(req, context=ctx, timeout=15).read().decode())
print(f'雲端現有: {len(patients)} 位')

changed = 0
for p in patients:
    if p.get('bed') == '示範':
        continue  # 示範病患不動
    if 'unit' not in p:
        p['unit'] = '國際桃庚'
        changed += 1

print(f'標記 {changed} 位為「國際桃庚」')

# 上傳
body = json.dumps(patients, ensure_ascii=False).encode('utf-8')
req2 = urllib.request.Request('https://hdr-note.vercel.app/api/patients',
    data=body, headers={'X-Password': pw, 'Content-Type': 'application/json'}, method='POST')
res = urllib.request.urlopen(req2, context=ctx, timeout=30).read().decode()
print(f'上傳結果: {res}')
