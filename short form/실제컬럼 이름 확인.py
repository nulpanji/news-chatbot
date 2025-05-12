import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# 1. 인증 정보 설정
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(
    "ivi-kdca-budget-auto-cca47dc30613.json", scope)
client = gspread.authorize(creds)

# 2. 구글 시트 열기
sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1w7Pho8uGw1dbIoS_0bAQXqvTXP5FfAEm14tSEuM4Cf4/edit")
worksheet = sheet.worksheet("scripts")  # 시트 이름

# 3. 데이터 읽기
data = worksheet.get_all_records()
df = pd.DataFrame(data)

# 4. 컬럼명 출력
print("📋 실제 컬럼명 리스트:")
print(df.columns.tolist())
