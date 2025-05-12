import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import re
from datetime import datetime
import os
from dotenv import load_dotenv
import pandas as pd

# 환경 변수 로드
load_dotenv()

# 고정된 링크 설정
COMMON_DOCS_LINK = "https://docs.google.com/spreadsheets/d/1l-nzSkIwpgHFfaDdqPoKWeK2HvhyxIKxCbNcz2oesDk/edit?usp=drive_link"
LECTURE_CERT_LINK = "https://docs.google.com/spreadsheets/d/11aZgFXTqlN9Kn2sktJP2Nqopgdp2G05ZIBjaaRykZsI/edit?usp=drive_link"
PPT_TEMPLATE_LINK = "https://drive.google.com/file/d/1Hac_nY7nc7kyd9Z09fojeEA4J127_XdCSu8Dhg-TznY/view?usp=sharing"
HANA_FONTS_LINK = "https://drive.google.com/file/d/182_ZEMQq6Swq1q10oFcCmCk4obRV-g6e/view?usp=sharing"

def is_valid_email(email):
    """이메일 형식 검사"""
    if not email or not isinstance(email, str):
        return False
    pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    return bool(re.match(pattern, email))

def send_instructor_emails(excel_path):
    """강사들에게 이메일 발송"""
    # 엑셀 파일 로드
    try:
        df = pd.read_excel(excel_path)
    except Exception as e:
        print(f"엑셀 파일 로드 오류: {e}")
        return
    
    # 필수 열 확인
    required_columns = ["강사명", "이메일", "발송여부", "이메일발송일자"]
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        print(f"다음 필수 열이 누락되었습니다: {', '.join(missing_columns)}")
        return
    
    # 이메일 설정
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = os.getenv("EMAIL_USER")
    sender_password = os.getenv("EMAIL_PASSWORD")
    reply_to = "hana2nd@sangsangwoori.com"
    
    if not sender_email or not sender_password:
        print("이메일 계정 정보가 설정되지 않았습니다. .env 파일을 확인하세요.")
        return
    
    # SMTP 서버 연결
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
    except Exception as e:
        print(f"SMTP 서버 연결 오류: {e}")
        return
    
    count = 0
    errors = []
    
    # 각 행 처리
    for idx, row in df.iterrows():
        # 이미 발송된 이메일은 건너뛰기
        if row.get("발송여부") == "발송 완료":
            print(f"행 {idx+2}: 이미 발송됨 ({row['이메일']})")
            continue
        
        name = row["강사명"]
        email = row["이메일"]
        
        # 이름 또는 이메일이 없으면 건너뛰기
        if pd.isna(name) or pd.isna(email):
            errors.append(f"행 {idx+2}: 이름 또는 이메일 누락")
            continue
        
        # 이메일 형식 검증
        if not is_valid_email(email):
            errors.append(f"행 {idx+2}: 이메일 형식이 잘못됨 ({email})")
            continue
        
        # 이메일 내용 구성
        subject = f"[상상우리] {name} 강사님, 교육 관련 서류를 전달드립니다"
        
        html_body = f"""<html><body>
<p>안녕하세요, {name} 강사님.</p>
<p>하나 파워 온 세컨드 라이프 교육 관련 제출 서류 및 자료를 전달드립니다.</p>
<ul>
<li>강사프로필과 증빙 사본 (1회 제출): <a href="{COMMON_DOCS_LINK}" target="_blank">링크</a></li>
<li>강의확인서 (출강 시 제출): <a href="{LECTURE_CERT_LINK}" target="_blank">링크</a></li>
<li>교재 템플릿 (PPT): <a href="{PPT_TEMPLATE_LINK}" target="_blank">링크</a></li>
<li>Hana Fonts (Zip): <a href="{HANA_FONTS_LINK}" target="_blank">링크</a></li>
</ul>
<p>작성 후 회신 부탁드립니다.<br>감사합니다.</p>
<p>- 상상우리 드림</p>
</body></html>"""
        
        # 이메일 메시지 생성
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = email
        msg['Subject'] = subject
        msg['Reply-To'] = reply_to
        
        msg.attach(MIMEText(html_body, 'html'))
        
        # 이메일 전송
        try:
            server.send_message(msg)
            
            # 발송 상태 및 날짜 업데이트
            df.at[idx, "발송여부"] = "발송 완료"
            df.at[idx, "이메일발송일자"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            count += 1
            print(f"행 {idx+2}: 이메일 발송 성공 ({email})")
        except Exception as e:
            errors.append(f"행 {idx+2}: 이메일 전송 오류 ({email}): {str(e)}")
    
    # SMTP 서버 연결 종료
    server.quit()
    
    # 업데이트된 데이터프레임 저장
    try:
        df.to_excel(excel_path, index=False)
        print(f"엑셀 파일 업데이트 완료: {excel_path}")
    except Exception as e:
        print(f"엑셀 파일 저장 오류: {e}")
    
    # 결과 출력
    print(f"\n총 {count}건의 이메일을 성공적으로 발송했습니다.")
    if errors:
        print("\n오류:")
        for error in errors:
            print(error)

def send_test_email():
    """테스트 이메일 발송"""
    # 이메일 설정
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = os.getenv("EMAIL_USER")
    sender_password = os.getenv("EMAIL_PASSWORD")
    reply_to = "hana2nd@sangsangwoori.com"
    
    if not sender_email or not sender_password:
        print("이메일 계정 정보가 설정되지 않았습니다. .env 파일을 확인하세요.")
        return
    
    # 수신자 정보
    name = input("테스트 이메일 수신자 이름: ")
    email = input("테스트 이메일 수신자 이메일: ")
    
    # 이메일 내용 구성
    subject = f"[상상우리] {name} 강사님, 교육 관련 서류를 전달드립니다"
    
    html_body = f"""<html><body>
<p>안녕하세요, {name} 강사님.</p>
<p>하나 파워 온 세컨드 라이프 교육 관련 제출 서류 및 자료를 전달드립니다.</p>
<ul>
<li>강사프로필과 증빙 사본 (1회 제출): <a href="{COMMON_DOCS_LINK}" target="_blank">링크</a></li>
<li>강의확인서 (출강 시 제출): <a href="{LECTURE_CERT_LINK}" target="_blank">링크</a></li>
<li>교재 템플릿 (PPT): <a href="{PPT_TEMPLATE_LINK}" target="_blank">링크</a></li>
<li>Hana Fonts (Zip): <a href="{HANA_FONTS_LINK}" target="_blank">링크</a></li>
</ul>
<p>작성 후 회신 부탁드립니다.<br>감사합니다.</p>
<p>- 상상우리 드림</p>
</body></html>"""
    
    # SMTP 서버 연결
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        
        # 이메일 메시지 생성
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = email
        msg['Subject'] = subject
        msg['Reply-To'] = reply_to
        
        msg.attach(MIMEText(html_body, 'html'))
        
        # 이메일 전송
        server.send_message(msg)
        print(f"테스트 이메일이 {email}로 성공적으로 발송되었습니다.")
        
        # SMTP 서버 연결 종료
        server.quit()
        
    except Exception as e:
        print(f"이메일 전송 오류: {str(e)}")

if __name__ == "__main__":
    print("이메일 발송 프로그램을 시작합니다.")
    print("1. 엑셀 파일에서 대량 발송")
    print("2. 테스트 이메일 발송")
    
    choice = input("선택하세요 (1 또는 2): ")
    
    if choice == "1":
        excel_path = input("엑셀 파일 경로를 입력하세요: ")
        send_instructor_emails(excel_path)
    elif choice == "2":
        send_test_email()
    else:
        print("잘못된 선택입니다.")
