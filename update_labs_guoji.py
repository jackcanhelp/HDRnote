"""
更新國際桃庚抽血資料
掃描 Patient/國際桃庚/Lab/ 下所有 .xls/.xlsx
支援兩種格式：
  格式A (一月/二月): row1=日期, row2=姓名, row3=日期重複, row4+=項目值
  格式B (三月/四月+舊格式): row1=姓名, row2=日期, row3+=項目值
年份：檔名有數字(11503)→民國年換算；中文月份名→民國115=2026
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

LAB_DIR = Path(__file__).parent / 'Patient' / '國際桃庚' / 'Lab'
SECRETS  = Path(__file__).parent / 'secrets.bat'

pw = ''
if SECRETS.exists():
    m = re.search(r'set\s+HDR_PASSWORD\s*=\s*(\S+)', SECRETS.read_text(), re.IGNORECASE)
    if m: pw = m.group(1)
if not pw:
    pw = input('請輸入 HDR_PASSWORD: ').strip()

result = {}

def get_year_month(filename, row0):
    """從檔名或 row0 取得 yearMonth 字串"""
    # 先嘗試數字格式: 11503 → 2026-03
    m = re.match(r'(\d{3})(\d{2})', Path(filename).name)
    if m:
        roc, mon = int(m.group(1)), int(m.group(2))
        return f"{roc + 1911}-{mon:02d}"
    # 從 row0[11] 取月份: "01 月份" → 01
    month_str = row0[11] if len(row0) > 11 else ''
    m2 = re.match(r'(\d{1,2})\s*月', month_str)
    if m2:
        mon = int(m2.group(1))
        return f"2026-{mon:02d}"
    return ''

def add_record(name, record):
    name = name.strip()
    if not name or name in ('項目', '日期/姓名', ''):
        return
    if name not in result:
        result[name] = []
    key = f"{record['yearMonth']}_{record.get('date','')}"
    if not any(f"{r['yearMonth']}_{r['date']}" == key for r in result[name]):
        result[name].append(record)

def parse_rows(rows, filename):
    if len(rows) < 3:
        return
    row0 = rows[0]
    ym = get_year_month(filename, row0)
    if not ym:
        print(f'  ⚠ 無法判斷年月，跳過 {filename}')
        return

    r1 = rows[1]
    r2 = rows[2]

    # 判斷格式
    if r1[0] in ('日期/姓名',):
        # 格式A: row1=日期, row2=姓名, row3=日期重複, data從row4
        dates = r1[1:]
        names = r2[1:]
        data_rows = rows[4:]
    elif r1[0] in ('項目',):
        # 格式B: row1=姓名, row2=日期, data從row3
        names = r1[1:]
        dates = r2[1:]
        data_rows = rows[3:]
    else:
        # 舊格式: row1=姓名, row2=日期, data從row3（同格式B）
        names = r1[1:]
        dates = r2[1:]
        data_rows = rows[3:]

    month_label = row0[11] if len(row0) > 11 else ''

    for col_i, name in enumerate(names):
        name = name.strip()
        if not name or name in ('', '—'):
            continue
        date_val = dates[col_i].strip() if col_i < len(dates) else ''
        record = {
            'yearMonth': ym,
            'period': month_label,
            'date': date_val,
        }
        for drow in data_rows:
            item = drow[0].strip() if drow else ''
            val = drow[col_i + 1].strip() if col_i + 1 < len(drow) else ''
            if item and val and item not in ('日期', ''):
                record[item] = val
        add_record(name, record)

# ── 解析所有 .xls ──
for f in sorted(LAB_DIR.glob('*.xls')):
    print(f'解析 {f.name}...')
    wb = xlrd.open_workbook(str(f))
    for si in range(wb.nsheets):
        ws = wb.sheet_by_index(si)
        rows = [[str(ws.cell_value(r, c)).strip() for c in range(ws.ncols)] for r in range(ws.nrows)]
        parse_rows(rows, f.name)

# ── 解析所有 .xlsx ──
for f in sorted(LAB_DIR.glob('*.xlsx')):
    print(f'解析 {f.name}...')
    wb2 = openpyxl.load_workbook(str(f))
    for sheet in wb2.worksheets:
        rows = [[str(c.value).strip() if c.value is not None else '' for c in row] for row in sheet.iter_rows()]
        parse_rows(rows, f.name)

for name in result:
    result[name].sort(key=lambda r: (r.get('yearMonth', ''), r.get('date', '')))

print(f'\n共解析 {len(result)} 位病人的抽血資料')

# ── 下載現有 labs，保留虛擬病患資料，合併本次解析結果 ──
ctx = ssl.create_default_context()
try:
    req_get = urllib.request.Request(
        'https://hdr-note.vercel.app/api/labs',
        headers={'X-Password': pw}, method='GET'
    )
    existing_labs = json.loads(urllib.request.urlopen(req_get, context=ctx, timeout=15).read().decode())
    print(f'雲端現有 {len(existing_labs)} 位病人的 lab 資料')
except Exception as e:
    print(f'無法取得現有 lab，從空白開始: {e}')
    existing_labs = {}

# 合併：用本次解析結果覆蓋同名病人，保留其他（虛擬病患等）
merged = {**existing_labs, **result}
print(f'合併後共 {len(merged)} 位病人')

# 儲存本地備份
out_path = LAB_DIR / 'labs.json'
out_path.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'已儲存本地備份: {out_path}')

# ── 上傳 ──
print('上傳到 Vercel...')
data = json.dumps(merged, ensure_ascii=False).encode('utf-8')
req_post = urllib.request.Request(
    'https://hdr-note.vercel.app/api/labs',
    data=data,
    headers={'Content-Type': 'application/json', 'X-Password': pw},
    method='POST'
)
try:
    resp = urllib.request.urlopen(req_post, context=ctx, timeout=60)
    print('上傳成功！', resp.read().decode())
except urllib.error.HTTPError as e:
    print('上傳失敗:', e.code, e.read().decode()[:200])
