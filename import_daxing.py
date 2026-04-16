"""
匯入大興鑫庚病患名單 (鑫庚115.xlsx)
格式：左半=QW135(週一三五) A=早/B=中/C=晚，右半=QW246(週二四六) A=早/B=中
"""
import openpyxl, json, urllib.request, ssl, re, time
from pathlib import Path

SECRETS = Path(__file__).parent / 'secrets.bat'
pw = ''
if SECRETS.exists():
    m = re.search(r'set\s+HDR_PASSWORD\s*=\s*(\S+)', SECRETS.read_text(), re.IGNORECASE)
    if m: pw = m.group(1)

ctx = ssl.create_default_context()

# ── 讀取 Excel ──
wb = openpyxl.load_workbook('Patient/大興鑫庚/鑫庚115.xlsx')
ws = wb.active
rows = [list(r) for r in ws.iter_rows(values_only=True)]

UNIT = '大興鑫庚'
new_patients = []
seq = 1  # 流水號

def clean(v):
    if v is None: return None
    s = str(v).strip()
    return None if s in ('', '—', '-', '－') else s

def make_patient(name, bed, qw, shift):
    global seq
    pid = f'DX{seq:04d}'
    seq += 1
    return {
        'patientId': pid,
        'name': name,
        'unit': UNIT,
        'bed': str(bed),
        'qw': qw,
        'shift': shift,
        'gender': '',
        'birthday': '',
        'idNumber': '',
        'frequency': 3,
        'duration': 4,
        'ak': '',
        'dialysate': '',
        'accessSide': '',
        'accessLocation': '',
        'accessType': '',
        'heparinDose': 0,
        'bloodFlow': 0,
        'dw': 0,
        'bloodType': '',
        'chronicDiseases': '',
        'drugAllergies': 'nil',
        'firstDialysisHospital': '',
        'firstDialysisDate': '',
        'medications': [],
        'medicationHistory': {},
        'dialysisRecords': [],
        'reminders': '',
        'todos': [],
        'isActive': True,
    }

# 資料從 row index 2 開始（0=標題, 1=欄位名）
# 最後幾行是備注，跳過
for row in rows[2:]:
    bed_w1 = clean(row[0])
    name_w1_A = clean(row[1])  # 早
    name_w1_B = clean(row[2])  # 中
    name_w1_C = clean(row[3])  # 晚
    bed_w2 = clean(row[6])
    name_w2_A = clean(row[7])  # 早
    name_w2_B = clean(row[8])  # 中

    # 跳過非床位行（備注等）
    if bed_w1 and not str(bed_w1).startswith('人數') and not str(bed_w1).startswith('注意') and not str(bed_w1).startswith('閱後'):
        if name_w1_A: new_patients.append(make_patient(name_w1_A, bed_w1, 'QW135', '早'))
        if name_w1_B: new_patients.append(make_patient(name_w1_B, bed_w1, 'QW135', '中'))
        if name_w1_C: new_patients.append(make_patient(name_w1_C, bed_w1, 'QW135', '晚'))

    if bed_w2 and not str(bed_w2).startswith('人數') and not str(bed_w2).startswith('注意') and not str(bed_w2).startswith('閱後'):
        if name_w2_A: new_patients.append(make_patient(name_w2_A, bed_w2, 'QW246', '早'))
        if name_w2_B: new_patients.append(make_patient(name_w2_B, bed_w2, 'QW246', '中'))

print(f'解析到 {len(new_patients)} 位大興鑫庚病患')

# ── 下載現有資料 ──
req = urllib.request.Request('https://hdr-note.vercel.app/api/patients',
    headers={'X-Password': pw}, method='GET')
existing = json.loads(urllib.request.urlopen(req, context=ctx, timeout=15).read().decode())
print(f'雲端現有: {len(existing)} 位')

# 移除舊的大興鑫庚資料（避免重複）
existing = [p for p in existing if p.get('unit') != UNIT]
combined = existing + new_patients
print(f'合併後共: {len(combined)} 位')

# 預覽前幾筆
for p in new_patients[:5]:
    print(f"  {p['patientId']} {p['name']} 床{p['bed']} {p['qw']} {p['shift']}班")

# ── 上傳 ──
body = json.dumps(combined, ensure_ascii=False).encode('utf-8')
req2 = urllib.request.Request('https://hdr-note.vercel.app/api/patients',
    data=body, headers={'X-Password': pw, 'Content-Type': 'application/json'}, method='POST')
res = urllib.request.urlopen(req2, context=ctx, timeout=30).read().decode()
print(f'上傳結果: {res}')
