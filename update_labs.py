"""
更新抽血資料腳本
檔名格式：11503腎友抽血彙總.xls → 民國115年03月 → 西元2026-03
使用方式：把新的 .xls/.xlsx 放到 Patient/Lab/ 後雙擊 update_labs.bat
"""
import json, urllib.request, ssl, re
from pathlib import Path

try:
    import xlrd
except ImportError:
    import subprocess, sys
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'xlrd', 'openpyxl', '-q'])
    import xlrd

import openpyxl

LAB_DIR = Path(__file__).parent / 'Patient' / 'Lab'
SECRETS  = Path(__file__).parent / 'secrets.bat'

pw = ''
if SECRETS.exists():
    m = re.search(r'set\s+HDR_PASSWORD\s*=\s*(\S+)', SECRETS.read_text(), re.IGNORECASE)
    if m: pw = m.group(1)
if not pw:
    pw = input('請輸入 HDR_PASSWORD: ').strip()

result = {}  # { 病人名: [ {yearMonth, period, date, 項目: 值, ...} ] }

def extract_year_month(filename):
    """從 11503... 解析民國年月 → 西元 yearMonth 字串"""
    m = re.match(r'(\d{3})(\d{2})', Path(filename).name)
    if m:
        roc, mon = int(m.group(1)), int(m.group(2))
        return f"{roc + 1911}-{mon:02d}"
    return ''

def parse_sheet(ws_rows, year_month, month_label):
    if len(ws_rows) < 3: return
    names = ws_rows[1][1:]
    dates = ws_rows[2][1:]
    for col_i, name in enumerate(names):
        name = name.strip()
        if not name or name == '項目': continue
        record = {
            'yearMonth': year_month,
            'period':    month_label,
            'date':      dates[col_i].strip() if col_i < len(dates) else ''
        }
        for row in ws_rows[3:]:
            item = row[0].strip()
            val  = row[col_i+1].strip() if col_i+1 < len(row) else ''
            if item and val:
                record[item] = val
        if name not in result:
            result[name] = []
        # 避免重複（同 yearMonth + 同 date 的記錄只保留一筆）
        key = f"{year_month}_{dates[col_i] if col_i < len(dates) else ''}"
        existing = [r for r in result[name] if f"{r['yearMonth']}_{r['date']}" == key]
        if not existing:
            result[name].append(record)

for f in sorted(LAB_DIR.glob('*.xls')):
    print(f'解析 {f.name}...')
    ym = extract_year_month(f.name)
    wb = xlrd.open_workbook(str(f))
    for si in range(wb.nsheets):
        ws = wb.sheet_by_index(si)
        rows = [[str(ws.cell_value(r,c)).strip() for c in range(ws.ncols)] for r in range(ws.nrows)]
        month_label = rows[0][11] if rows and len(rows[0]) > 11 else ''
        parse_sheet(rows, ym, month_label)

for f in sorted(LAB_DIR.glob('*.xlsx')):
    print(f'解析 {f.name}...')
    ym = extract_year_month(f.name)
    wb = openpyxl.load_workbook(str(f))
    for sheet in wb.worksheets:
        rows = [[str(c.value).strip() if c.value is not None else '' for c in row] for row in sheet.iter_rows()]
        month_label = rows[0][11] if rows and len(rows[0]) > 11 else ''
        parse_sheet(rows, ym, month_label)

# 每位病人的記錄依 yearMonth 排序
for name in result:
    result[name].sort(key=lambda r: (r.get('yearMonth',''), r.get('date','')))

out_path = LAB_DIR / 'labs.json'
out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'產生 labs.json：共 {len(result)} 位病人')

print('上傳到 Vercel...')
data = json.dumps(result).encode('utf-8')
ctx  = ssl.create_default_context()
req  = urllib.request.Request(
    'https://hdr-note.vercel.app/api/labs',
    data=data,
    headers={'Content-Type': 'application/json', 'X-Password': pw},
    method='POST'
)
try:
    resp = urllib.request.urlopen(req, context=ctx, timeout=60)
    print('上傳成功！', resp.read().decode())
except urllib.error.HTTPError as e:
    print('上傳失敗:', e.code, e.read().decode()[:200])

input('\n按 Enter 關閉...')
