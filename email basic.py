# email_basic.py
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# Google Sheets 연결 설정
scope = ['[https://spreadsheets.google.com/feeds',](https://spreadsheets.google.com/feeds',) '[https://www.googleapis.com/auth/drive']](https://www.googleapis.com/auth/drive'])
print("설정 완료:", scope)

# 이메일 설정
smtp_server = "smtp.gmail.com"
smtp_port = 587
sender_email = os.getenv("EMAIL_USER")
sender_password = os.getenv("EMAIL_PASSWORD")

print("이메일 설정:", sender_email)

if __name__ == "__main__":
    print("이메일 발송 프로그램을 시작합니다.")
    print("1. Google 스프레드시트에서 대량 발송")
    print("2. 테스트 이메일 발송")
    
    choice = input("선택하세요 (1 또는 2): ")
    print(f"선택한 옵션: {choice}")