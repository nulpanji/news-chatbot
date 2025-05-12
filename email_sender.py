import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
from dotenv import load_dotenv
from datetime import datetime

# 환경 변수 로드 (.env 파일 필요)
load_dotenv()

# 구글 시트 API 스코프
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

# 구글 서비스 계정 키 파일 경로
credentials_path = 'credentials.json'  # 반드시 본인 파일명으로 수정

def is_valid_email(email):
    import re
    pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    return bool(re.match(pattern, str(email)))

def send_emails(sheet_id):
    # 구글 시트 연결
    credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
    client = gspread.authorize(credentials)
    worksheet = client.open_by_key(sheet_id).sheet1
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)
    
    # 이메일 계정 정보
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = os.getenv("EMAIL_USER")
    sender_password = os.getenv("EMAIL_PASSWORD")
    reply_to = "hana2nd@sangsangwoori.com"
    
    if not sender_email or not sender_password:
        print("이메일 계정 정보가 없습니다. .env 파일을 확인하세요.")
        return
    
    # SMTP 서버 연결
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(sender_email, sender_password)
    
    count = 0
    for idx, row in df.iterrows():
        if row.get("발송여부") == "발송 완료":
            continue
        name = row["강사명"]
        email = row["이메일"]
        if not is_valid_email(email):
            print(f"잘못된 이메일: {email}")
            continue
        subject = f"[상상우리] {name} 강사님, 교육 관련 서류를 전달드립니다"
        html_content = f"""
        <html><body>
        <p>안녕하세요, {name} 강사님.</p>
        <p>하나 파워 온 세컨드 라이프 교육 관련 제출 서류 및 자료를 전달드립니다.</p>
        <ul>
        <li>강사프로필과 증빙 사본 (1회 제출): <a href="https://docs.google.com/spreadsheets/d/1l-nzSkIwpgHFfaDdqPoKWeK2HvhyxIKxCbNcz2oesDk/edit">링크</a></li>
        <li>강의확인서 (출강 시 제출): <a href="https://docs.google.com/spreadsheets/d/11aZgFXTqlN9Kn2sktJP2Nqopgdp2G05ZIBjaaRykZsI/edit">링크</a></li>
        <li>교재 템플릿 (PPT): <a href="https://drive.google.com/file/d/1Hac_nY7nc7kyd9Z09fojeEA4J127_XdCSu8Dhg-TznY/view">링크</a></li>
        <li>Hana Fonts (Zip): <a href="https://drive.google.com/file/d/182_ZEMQq6Swq1q10oFcCmCk4obRV-g6e/view">링크</a></li>
        </ul>
        <p>작성 후 회신 부탁드립니다.<br>감사합니다.</p>
        <p>- 상상우리 드림</p>
        </body></html>
        """
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = email
        msg['Subject'] = subject
        msg['Reply-To'] = reply_to
        msg.attach(MIMEText(html_content, 'html'))
        try:
            server.send_message(msg)
            worksheet.update_cell(idx+2, df.columns.get_loc("발송여부")+1, "발송 완료")
            worksheet.update_cell(idx+2, df.columns.get_loc("이메일발송일자")+1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            print(f"{email} 발송 완료")
            count += 1
        except Exception as e:
            print(f"{email} 발송 실패: {e}")
    server.quit()
    print(f"총 {count}건 발송 완료")

if __name__ == "__main__":
    sheet_id = input("구글 시트 ID를 입력하세요: ")
    send_emails(sheet_id)
