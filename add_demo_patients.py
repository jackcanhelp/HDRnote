import json, urllib.request, ssl, re
from datetime import datetime
from pathlib import Path

SECRETS = Path(__file__).parent / 'secrets.bat'
pw = ''
if SECRETS.exists():
    m = re.search(r'set\s+HDR_PASSWORD\s*=\s*(\S+)', SECRETS.read_text(), re.IGNORECASE)
    if m: pw = m.group(1)

ctx = ssl.create_default_context()
now = datetime.now().isoformat()

# 下載現有資料
req = urllib.request.Request('https://hdr-note.vercel.app/api/patients',
    headers={'X-Password': pw}, method='GET')
existing = json.loads(urllib.request.urlopen(req, context=ctx, timeout=15).read().decode())
print(f'雲端現有: {len(existing)} 位')

test_patients = [
  {
    'patientId': 'P001234', 'name': '林小明', 'gender': '男', 'birthday': '1965-03-15',
    'idNumber': 'A123456789', 'frequency': 3, 'duration': 4, 'ak': 'FX80',
    'dialysate': 'Kt/V 1.4', 'accessSide': '左', 'accessLocation': '前臂', 'accessType': 'AVF',
    'heparinDose': 3000, 'bloodFlow': 280, 'dw': 65.5, 'bloodType': 'A+',
    'chronicDiseases': '糖尿病、高血壓、慢性腎衰竭', 'drugAllergies': '盤尼西林',
    'firstDialysisHospital': '台大醫院', 'firstDialysisDate': '2020-03-15',
    'bed': '示範', 'qw': 'QW135', 'shift': '早', 'reminders': '', 'todos': [],
    'medications': [
      {'id': 'med1', 'drugName': 'Calcitriol', 'dosage': '0.25', 'unit': 'mcg', 'quantity': 30,
       'frequency': '每日一次', 'monthlyStatus': 'prescribed', 'hospital': '台大醫院',
       'lastUpdated': '2025-06-01', 'category': 'dialysis'},
      {'id': 'med2', 'drugName': 'Sevelamer', 'dosage': '800', 'unit': 'mg', 'quantity': 90,
       'frequency': '每日三次', 'monthlyStatus': 'remaining', 'hospital': '台大醫院',
       'lastUpdated': '2025-05-15', 'category': 'dialysis'}
    ],
    'medicationHistory': {
      '2025': {'med1': {1:'prescribed',2:'prescribed',3:'prescribed',4:'prescribed',5:'prescribed',6:'prescribed'},
               'med2': {1:'prescribed',2:'prescribed',3:'remaining',4:'remaining',5:'remaining',6:'remaining'}},
      '2024': {'med1': {1:'prescribed',2:'prescribed',3:'prescribed',4:'prescribed',5:'prescribed',6:'prescribed',7:'prescribed',8:'prescribed',9:'prescribed',10:'prescribed',11:'prescribed',12:'prescribed'},
               'med2': {1:'prescribed',2:'prescribed',3:'prescribed',4:'prescribed',5:'prescribed',6:'prescribed',7:'prescribed',8:'prescribed',9:'remaining',10:'remaining',11:'remaining',12:'remaining'}}
    },
    'dialysisRecords': [
      {'id': 'dr1', 'date': '2025-06-01', 'startTime': '08:00', 'endTime': '12:00', 'duration': 4.0,
       'artificialKidney': 'FX80', 'dialysate': 'K2.0 Ca1.25', 'accessSide': '左', 'accessLocation': '前臂', 'accessType': 'AVF',
       'heparinDose': 3000, 'bloodFlow': 280, 'preWeight': 67.2, 'clothingWeight': 1.5, 'postWeight': 65.5, 'dryWeight': 65.5,
       'fluidRemoval': 1.7, 'temperature': 36.8, 'notes': '透析順利，無不適症狀',
       'processRecords': [
         {'id':'pr1','time':'08:00','systolicBP':140,'diastolicBP':80,'heartRate':78,'bloodFlow':280,'fluidRemovalRate':0.4,'specialNote':'開始透析，病人狀態穩定'},
         {'id':'pr2','time':'10:00','systolicBP':130,'diastolicBP':75,'heartRate':82,'bloodFlow':280,'fluidRemovalRate':0.5,'specialNote':''},
         {'id':'pr3','time':'11:30','systolicBP':110,'diastolicBP':65,'heartRate':85,'bloodFlow':280,'fluidRemovalRate':0.3,'specialNote':'血壓下降，調整脫水速度'}
       ]},
      {'id': 'dr2', 'date': '2025-05-30', 'startTime': '08:00', 'endTime': '12:00', 'duration': 4.0,
       'artificialKidney': 'FX80', 'dialysate': 'K2.0 Ca1.25', 'accessSide': '左', 'accessLocation': '前臂', 'accessType': 'AVF',
       'heparinDose': 3000, 'bloodFlow': 280, 'preWeight': 67.8, 'clothingWeight': 1.5, 'postWeight': 66.0, 'dryWeight': 65.5,
       'fluidRemoval': 1.8, 'temperature': 36.5, 'notes': '中途血壓略低，已調整',
       'processRecords': [
         {'id':'pr4','time':'08:00','systolicBP':135,'diastolicBP':85,'heartRate':75,'bloodFlow':280,'fluidRemovalRate':0.4,'specialNote':'開始透析'},
         {'id':'pr5','time':'10:30','systolicBP':105,'diastolicBP':60,'heartRate':88,'bloodFlow':250,'fluidRemovalRate':0.2,'specialNote':'血壓偏低，調整血流量'}
       ]}
    ],
    'isActive': True, 'createdAt': now, 'updatedAt': now
  },
  {
    'patientId': 'P002468', 'name': '陳小蓮', 'gender': '女', 'birthday': '1958-08-22',
    'idNumber': 'B987654321', 'frequency': 3, 'duration': 4.5, 'ak': 'FX100',
    'dialysate': 'Kt/V 1.2', 'accessSide': '右', 'accessLocation': '上臂', 'accessType': 'AVG',
    'heparinDose': 2500, 'bloodFlow': 250, 'dw': 58.2, 'bloodType': 'O-',
    'chronicDiseases': '多囊性腎病、高血壓', 'drugAllergies': '無已知過敏',
    'firstDialysisHospital': '榮總醫院', 'firstDialysisDate': '2018-08-22',
    'bed': '示範', 'qw': 'QW246', 'shift': '早', 'reminders': '', 'todos': [],
    'medications': [
      {'id': 'med3', 'drugName': 'EPO注射液', 'dosage': '4000', 'unit': 'IU', 'quantity': 4,
       'frequency': '每週一次', 'monthlyStatus': 'prescribed', 'hospital': '榮總醫院',
       'lastUpdated': '2025-06-01', 'category': 'dialysis'}
    ],
    'medicationHistory': {
      '2025': {'med3': {1:'prescribed',2:'prescribed',3:'prescribed',4:'prescribed',5:'prescribed',6:'prescribed'}},
      '2024': {'med3': {1:'prescribed',2:'prescribed',3:'prescribed',4:'prescribed',5:'prescribed',6:'prescribed',7:'prescribed',8:'prescribed',9:'prescribed',10:'prescribed',11:'prescribed',12:'prescribed'}}
    },
    'dialysisRecords': [
      {'id': 'dr3', 'date': '2025-06-01', 'startTime': '13:30', 'endTime': '18:00', 'duration': 4.5,
       'artificialKidney': 'FX100', 'dialysate': 'K2.0 Ca1.25', 'accessSide': '右', 'accessLocation': '上臂', 'accessType': 'AVG',
       'heparinDose': 2500, 'bloodFlow': 250, 'preWeight': 60.5, 'clothingWeight': 1.2, 'postWeight': 58.2, 'dryWeight': 58.2,
       'fluidRemoval': 2.3, 'temperature': 36.9, 'notes': '透析過程順利',
       'processRecords': [
         {'id':'pr6','time':'13:30','systolicBP':145,'diastolicBP':90,'heartRate':72,'bloodFlow':250,'fluidRemovalRate':0.5,'specialNote':'開始透析'},
         {'id':'pr7','time':'16:00','systolicBP':130,'diastolicBP':80,'heartRate':76,'bloodFlow':250,'fluidRemovalRate':0.5,'specialNote':'狀態穩定'}
       ]}
    ],
    'isActive': True, 'createdAt': now, 'updatedAt': now
  },
  {
    'patientId': 'P003579', 'name': '吳大山', 'gender': '男', 'birthday': '1972-12-10',
    'idNumber': 'C123789456', 'frequency': 2, 'duration': 5, 'ak': 'FX60',
    'dialysate': 'Kt/V 1.3', 'accessSide': '左', 'accessLocation': '上臂', 'accessType': 'Permcath',
    'heparinDose': 4000, 'bloodFlow': 300, 'dw': 72.8, 'bloodType': 'B+',
    'chronicDiseases': '慢性腎病、糖尿病', 'drugAllergies': '磺胺類藥物',
    'firstDialysisHospital': '長庚醫院', 'firstDialysisDate': '2019-06-01',
    'bed': '示範', 'qw': 'QW135', 'shift': '晚',
    'reminders': '轉院通知：已轉至其他醫院\n轉院日期：2025/6/1', 'todos': [],
    'medications': [
      {'id': 'med4', 'drugName': 'Insulin', 'dosage': '10', 'unit': 'unit', 'quantity': 1,
       'frequency': '每日一次', 'monthlyStatus': 'discontinued', 'hospital': '長庚醫院',
       'lastUpdated': '2025-05-20', 'category': 'internal'}
    ],
    'medicationHistory': {
      '2025': {'med4': {1:'prescribed',2:'prescribed',3:'prescribed',4:'prescribed',5:'discontinued',6:'discontinued'}},
      '2024': {'med4': {1:'prescribed',2:'prescribed',3:'prescribed',4:'prescribed',5:'prescribed',6:'prescribed',7:'prescribed',8:'prescribed',9:'prescribed',10:'prescribed',11:'prescribed',12:'prescribed'}}
    },
    'dialysisRecords': [
      {'id': 'dr4', 'date': '2025-05-20', 'startTime': '14:00', 'endTime': '19:00', 'duration': 5.0,
       'artificialKidney': 'FX60', 'dialysate': 'K2.0 Ca1.25', 'accessSide': '左', 'accessLocation': '上臂', 'accessType': 'Permcath',
       'heparinDose': 4000, 'bloodFlow': 300, 'preWeight': 74.8, 'clothingWeight': 2.0, 'postWeight': 72.8, 'dryWeight': 72.8,
       'fluidRemoval': 2.0, 'temperature': 37.1, 'notes': '最後一次透析，已轉院',
       'processRecords': [
         {'id':'pr8','time':'14:00','systolicBP':160,'diastolicBP':95,'heartRate':80,'bloodFlow':300,'fluidRemovalRate':0.4,'specialNote':'開始透析，血壓偏高'},
         {'id':'pr9','time':'17:00','systolicBP':140,'diastolicBP':85,'heartRate':78,'bloodFlow':300,'fluidRemovalRate':0.4,'specialNote':'最後一次透析，準備轉院'}
       ]}
    ],
    'isActive': False, 'createdAt': now, 'updatedAt': now
  },
  {
    'patientId': 'P004680', 'name': '張美枝', 'gender': '女', 'birthday': '1963-05-18',
    'idNumber': 'D456123789', 'frequency': 3, 'duration': 4, 'ak': 'FX80',
    'dialysate': 'Kt/V 1.5', 'accessSide': '右', 'accessLocation': '前臂', 'accessType': 'AVF',
    'heparinDose': 2800, 'bloodFlow': 270, 'dw': 60.3, 'bloodType': 'AB-',
    'chronicDiseases': '高血壓、慢性腎衰竭', 'drugAllergies': '無已知過敏',
    'firstDialysisHospital': '馬偕醫院', 'firstDialysisDate': '2021-02-14',
    'bed': '示範', 'qw': 'QW246', 'shift': '中', 'reminders': '', 'todos': [],
    'medications': [
      {'id': 'med5', 'drugName': 'Amlodipine', 'dosage': '5', 'unit': 'mg', 'quantity': 28,
       'frequency': '每日一次', 'monthlyStatus': 'prescribed', 'hospital': '馬偕醫院',
       'lastUpdated': '2025-06-01', 'category': 'internal'},
      {'id': 'med6', 'drugName': 'Phosphate Binder', 'dosage': '500', 'unit': 'mg', 'quantity': 60,
       'frequency': '每日兩次', 'monthlyStatus': 'remaining', 'hospital': '馬偕醫院',
       'lastUpdated': '2025-05-20', 'category': 'dialysis'}
    ],
    'medicationHistory': {
      '2025': {'med5': {1:'prescribed',2:'prescribed',3:'prescribed',4:'prescribed',5:'prescribed',6:'prescribed'},
               'med6': {1:'prescribed',2:'prescribed',3:'remaining',4:'remaining',5:'remaining',6:'remaining'}},
      '2024': {'med5': {1:'prescribed',2:'prescribed',3:'prescribed',4:'prescribed',5:'prescribed',6:'prescribed',7:'prescribed',8:'prescribed',9:'prescribed',10:'prescribed',11:'prescribed',12:'prescribed'},
               'med6': {1:'prescribed',2:'prescribed',3:'prescribed',4:'prescribed',5:'prescribed',6:'prescribed',7:'prescribed',8:'prescribed',9:'remaining',10:'remaining',11:'remaining',12:'remaining'}}
    },
    'dialysisRecords': [
      {'id': 'dr5', 'date': '2025-06-01', 'startTime': '08:00', 'endTime': '12:00', 'duration': 4.0,
       'artificialKidney': 'FX80', 'dialysate': 'K2.0 Ca1.25', 'accessSide': '右', 'accessLocation': '前臂', 'accessType': 'AVF',
       'heparinDose': 2800, 'bloodFlow': 270, 'preWeight': 62.1, 'clothingWeight': 1.5, 'postWeight': 60.3, 'dryWeight': 60.3,
       'fluidRemoval': 1.8, 'temperature': 36.7, 'notes': '透析效果良好',
       'processRecords': [
         {'id':'pr10','time':'08:00','systolicBP':125,'diastolicBP':75,'heartRate':70,'bloodFlow':270,'fluidRemovalRate':0.4,'specialNote':'開始透析'},
         {'id':'pr11','time':'10:00','systolicBP':120,'diastolicBP':70,'heartRate':72,'bloodFlow':270,'fluidRemovalRate':0.5,'specialNote':'狀態良好'},
         {'id':'pr12','time':'12:00','systolicBP':115,'diastolicBP':68,'heartRate':74,'bloodFlow':270,'fluidRemovalRate':0.2,'specialNote':'透析結束，狀態穩定'}
       ]}
    ],
    'isActive': True, 'createdAt': now, 'updatedAt': now
  }
]

combined = existing + test_patients
print(f'合併後共 {len(combined)} 位（{len(existing)} 真實 + {len(test_patients)} 示範）')

data = json.dumps(combined).encode('utf-8')
req2 = urllib.request.Request('https://hdr-note.vercel.app/api/patients', data=data,
    headers={'Content-Type': 'application/json', 'X-Password': pw}, method='POST')
resp = urllib.request.urlopen(req2, context=ctx, timeout=30)
print('上傳:', resp.read().decode())
