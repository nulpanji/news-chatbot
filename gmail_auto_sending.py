import re
from datetime import datetime
import os
import json
import gspread
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def is_valid_email(email):
    """이메일 형식 검사"""
    if not email or not isinstance(email, str):
        return False
    pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    return bool(re.match(pattern, email))

def send_instructor_emails(sheet_id):
    """강사들에게 이메일 발송"""
    # Google Sheets 및 Gmail API 연결 설정
    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/gmail.send',
        'https://www.googleapis.com/auth/gmail.compose',
        'https://mail.google.com/',
        'https://www.googleapis.com/auth/gmail.modify'
    ]
    
    # 기존 토큰 파일 삭제 (권한 문제 해결을 위해)
    if os.path.exists('token.json'):
        try:
            os.remove('token.json')
            print("기존 토큰을 삭제하고 새로 인증합니다...")
        except Exception as e:
            print(f"토큰 파일 삭제 오류: {e}")
    
    # OAuth 2.0 클라이언트 ID 사용
    creds = None
    
    # 토큰이 있으면 로드
    if os.path.exists('token.json'):
        try:
            with open('token.json', 'r') as token_file:
                token_data = token_file.read()
                if token_data.strip():
                    creds = Credentials.from_authorized_user_info(
                        json.loads(token_data), SCOPES)
        except (json.JSONDecodeError, ValueError) as e:
            print(f"토큰 파일 오류: {e}")
            print("새로운 토큰을 생성합니다...")
            # 손상된 토큰 파일 삭제
            if os.path.exists('token.json'):
                os.remove('token.json')
    
    # 토큰이 없거나 유효하지 않으면 새로 생성
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # client_secret.json 파일 확인
            if not os.path.exists('client_secret.json'):
                print("오류: client_secret.json 파일이 없습니다.")
                print("Google Cloud Console에서 OAuth 클라이언트 ID를 다운로드하고 'client_secret.json'으로 이름 변경하여")
                print("C:\\Users\\LG\\Documents\\Windsurf 폴더에 저장하세요.")
                return
                
            flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # 토큰 저장
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    try:
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_key(sheet_id)
        worksheet = spreadsheet.sheet1  # 첫 번째 시트 사용
        
        # 현재 스프레드시트의 헤더(첫 번째 행) 가져오기
        headers = worksheet.row_values(1)
        
        # 필수 열 확인 및 누락된 열 추가
        required_columns = ["강사명", "이메일", "발송여부", "이메일발송일자"]
        missing_columns = [col for col in required_columns if col not in headers]
        
        # 누락된 열이 있으면 추가
        if missing_columns:
            print(f"다음 열이 누락되어 자동으로 추가합니다: {', '.join(missing_columns)}")
            for col in missing_columns:
                # 새 열 추가
                next_col = len(headers) + 1
                worksheet.update_cell(1, next_col, col)
                headers.append(col)
            
            # 스프레드시트 변경사항 적용을 위해 잠시 대기
            print("스프레드시트 업데이트 중...")
            import time
            time.sleep(2)
        
        # 데이터 다시 가져오기
        data = worksheet.get_all_records()  # 이미 리스트의 딩셔너리 형태
    except Exception as e:
        print(f"Google 스프레드시트 연결 오류: {e}")
        return

    # Gmail API를 사용하여 이메일 발송 (인코딩 문제 해결)
    # 이미 인증된 OAuth 토큰을 사용하여 Gmail API 연결
    try:
        # Gmail API 서비스 생성
        service = build('gmail', 'v1', credentials=creds)
        # 사용자 프로필에서 이메일 주소 가져오기
        sender_email = service.users().getProfile(userId='me').execute().get('emailAddress')
        
        reply_to = "hana2nd@sangsangwoori.com"
    except Exception as e:
        print(f"Gmail API 연결 오류: {e}")
        return

    count = 0
    errors = []
    updates = []

    # 비어 있는 행 건너뛰기
    print("스프레드시트 데이터 처리 중...")
    valid_rows = []
    for idx, row in enumerate(data):
        # 새로운 헤더 구조: 강사명, 연락번호, 이메일, 일자리분야, 과정명, ...
        name = row.get("강사명")
        email = row.get("이메일")
        
        # 발송여부 열이 삭제되었으므로 발송여부 검사 제거
            
        # 비어 있는 행 처리
        if not name or not email or name.strip() == "" or email.strip() == "":
            # 비어 있는 행은 오류 메시지 출력하지 않고 그냥 건너뛀
            continue
            
        # 유효한 행만 처리 대상에 추가
        valid_rows.append((idx, row))
    
    print(f"처리할 유효한 행: {len(valid_rows)}개")
    
    # 유효한 행만 처리
    for idx, row in valid_rows:
        # 새로운 헤더 구조: 강사명, 연락번호, 이메일, 일자리분야, 과정명, ...
        name = row.get("강사명")
        email = row.get("이메일")

        if not is_valid_email(email):
            errors.append(f"행 {idx+2}: 이메일 형식이 잘못됨 ({email})")
            continue
            
        # 일자리분야와 과정명 정보 가져오기
        job_field = row.get("일자리분야", "")
        course_name = row.get("과정명", "")
        
        # 기본 링크 설정
        common_link = "https://docs.google.com/spreadsheets/d/1l-nzSkIwpgHFfaDdqPoKWeK2HvhyxIKxCbNcz2oesDk/edit"
        lecture_link = "https://docs.google.com/spreadsheets/d/11aZgFXTqlN9Kn2sktJP2Nqopgdp2G05ZIBjaaRykZsI/edit"
        
        print(f"행 {idx+2}: 일자리분야 = {job_field}, 과정명 = {course_name}")
        
        # 강의확인서 Only 체크박스 상태 확인 (새 헤더 구조에서는 8번째 열)
        lecture_confirm_only = row.get("강의확인서 Only", False)
        # 체크박스가 체크되어 있으면 True, 아니면 False
        # 구글 시트에서 체크박스는 'TRUE' 또는 'FALSE' 문자열로 나올 수 있음
        if isinstance(lecture_confirm_only, str):
            lecture_confirm_only = lecture_confirm_only.upper() == 'TRUE'
            
        # 발송보류 체크박스 상태 확인 (새 헤더 구조에서는 9번째 열)
        hold_sending = row.get("발송보류", False)
        if isinstance(hold_sending, str):
            hold_sending = hold_sending.upper() == 'TRUE'
            
        print(f"행 {idx+2}: 강의확인서 Only = {lecture_confirm_only}, 발송보류 = {hold_sending}")
        
        # 발송보류가 체크되어 있으면 이메일 발송하지 않음
        if hold_sending:
            errors.append(f"행 {idx+2}: 발송보류가 체크되어 있어 이메일을 발송하지 않습니다.")
            continue

        subject = f"[상상우리] {name} 강사님, "
        
        # 강의확인서 Only 체크박스 상태에 따라 제목과 내용 변경
        if lecture_confirm_only:
            subject += "강의확인서 전달드립니다"
            html_content = f"""<html><body>
<p>안녕하세요, {name} 강사님.</p>
<p>하나 파워 온 세컨드 라이프 교육 관련 강의확인서를 전달드립니다.</p>
<ul>
<li>강의확인서 (출강 시 제출): <a href="https://docs.google.com/spreadsheets/d/11aZgFXTqlN9Kn2sktJP2Nqopgdp2G05ZIBjaaRykZsI/edit">링크</a></li>
</ul>
<p>작성 후 회신 부탁드립니다.<br>감사합니다.</p>
<p>- 상상우리 드림</p>
</body></html>"""
        else:
            subject += "교육 관련 서류를 전달드립니다"
            html_content = f"""<html><body>
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
</body></html>"""

        # 이메일 메시지 생성 (한글 인코딩 문제 해결)
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = email
        # 제목에 한글이 있으므로 Header 클래스를 사용하여 인코딩 처리
        from email.header import Header
        msg['Subject'] = Header(subject, 'utf-8')
        msg['Reply-To'] = reply_to
        msg.attach(MIMEText(html_content, 'html', 'utf-8'))

        try:
            # Gmail API를 사용하여 이메일 발송
            raw_message = base64.urlsafe_b64encode(msg.as_bytes()).decode()
            message = {'raw': raw_message}
            service.users().messages().send(userId='me', body=message).execute()
            row_num = idx + 2
            # 헤더에서 열 위치 찾기 (헤더가 업데이트되었을 수 있음)
            headers = worksheet.row_values(1)
            col_status_idx = headers.index("발송여부") + 1 if "발송여부" in headers else None
            col_date_idx = headers.index("이메일발송일자") + 1 if "이메일발송일자" in headers else None
            
            update_data = {
                'row': row_num,
                'value_status': "발송 완료",
                'value_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            if col_status_idx:
                update_data['col_status'] = col_status_idx
            if col_date_idx:
                update_data['col_date'] = col_date_idx
                
            updates.append(update_data)
            count += 1
            print(f"행 {row_num}: 이메일 발송 성공 ({email})")
        except Exception as e:
            errors.append(f"행 {idx+2}: 이메일 전송 오류 ({email}): {str(e)}")

    # Gmail API는 연결 종료가 필요 없음

    try:
        for update in updates:
            # 발송 상태 및 날짜 업데이트
            if 'col_status' in update:
                worksheet.update_cell(update['row'], update['col_status'], update['value_status'])
            
            if 'col_date' in update:
                worksheet.update_cell(update['row'], update['col_date'], update['value_date'])
        print(f"Google 스프레드시트 업데이트 완료")
    except Exception as e:
        print(f"스프레드시트 업데이트 오류: {e}")

    print(f"\n총 {count}건의 이메일을 성공적으로 발송했습니다.")
    if errors:
        print("\n오류:")
        for error in errors:
            print(error)

def send_test_email():
    """테스트 이메일 발송"""
    # Google Sheets 및 Gmail API 연결 설정
    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/gmail.send',
        'https://www.googleapis.com/auth/gmail.compose',
        'https://mail.google.com/',
        'https://www.googleapis.com/auth/gmail.modify'
    ]
    
    # OAuth 2.0 클라이언트 ID 사용
    creds = None
    
    # 토큰이 있으면 로드
    if os.path.exists('token.json'):
        try:
            with open('token.json', 'r') as token_file:
                token_data = token_file.read()
                if token_data.strip():
                    creds = Credentials.from_authorized_user_info(
                        json.loads(token_data), SCOPES)
        except (json.JSONDecodeError, ValueError) as e:
            print(f"토큰 파일 오류: {e}")
            print("새로운 토큰을 생성합니다...")
            # 손상된 토큰 파일 삭제
            if os.path.exists('token.json'):
                os.remove('token.json')
    
    # 토큰이 없거나 유효하지 않으면 새로 생성
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # client_secret.json 파일 확인
            if not os.path.exists('client_secret.json'):
                print("오류: client_secret.json 파일이 없습니다.")
                print("Google Cloud Console에서 OAuth 클라이언트 ID를 다운로드하고 'client_secret.json'으로 이름 변경하여")
                print("C:\\Users\\LG\\Documents\\Windsurf 폴더에 저장하세요.")
                return
                
            flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # 토큰 저장
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    try:
        # Gmail API 서비스 생성
        service = build('gmail', 'v1', credentials=creds)
        # 사용자 프로필에서 이메일 주소 가져오기
        sender_email = service.users().getProfile(userId='me').execute().get('emailAddress')
        reply_to = "hana2nd@sangsangwoori.com"
    except Exception as e:
        print(f"Gmail API 연결 오류: {e}")
        return

    email = input("수신자 이메일 주소: ")
    if not is_valid_email(email):
        print("유효하지 않은 이메일 주소입니다.")
        return

    subject = "[상상우리] 테스트 이메일"
    html_content = f"""<html><body>
<p>안녕하세요, 테스트 이메일입니다.</p>
<p>하나 파워 온 세컨드 라이프 교육 관련 제출 서류 및 자료를 전달드립니다.</p>
<ul>
<li>강사프로필과 증빙 사본 (1회 제출): <a href="https://docs.google.com/spreadsheets/d/1l-nzSkIwpgHFfaDdqPoKWeK2HvhyxIKxCbNcz2oesDk/edit">링크</a></li>
<li>강의확인서 (출강 시 제출): <a href="https://docs.google.com/spreadsheets/d/11aZgFXTqlN9Kn2sktJP2Nqopgdp2G05ZIBjaaRykZsI/edit">링크</a></li>
<li>교재 템플릿 (PPT): <a href="https://drive.google.com/file/d/1Hac_nY7nc7kyd9Z09fojeEA4J127_XdCSu8Dhg-TznY/view">링크</a></li>
<li>Hana Fonts (Zip): <a href="https://drive.google.com/file/d/182_ZEMQq6Swq1q10oFcCmCk4obRV-g6e/view">링크</a></li>
</ul>
<p>작성 후 회신 부탁드립니다.<br>감사합니다.</p>
<p>- 상상우리 드림</p>
</body></html>"""

    try:
        # 이메일 메시지 생성
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = email
        from email.header import Header
        msg['Subject'] = Header(subject, 'utf-8')
        msg['Reply-To'] = reply_to
        msg.attach(MIMEText(html_content, 'html', 'utf-8'))
        
        # Gmail API를 사용하여 이메일 발송
        raw_message = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        message = {'raw': raw_message}
        service.users().messages().send(userId='me', body=message).execute()
        print(f"테스트 이메일이 {email}로 성공적으로 발송되었습니다.")
    except Exception as e:
        print(f"이메일 전송 오류: {str(e)}")

if __name__ == "__main__":
    # 고정 스프레드시트 ID
    DEFAULT_SHEET_ID = "1hpKlmzxVsTldkGx7kTkIxsrmAvRMThfK3zrt0bh_6zQ"
    
    print("이메일 발송 프로그램을 시작합니다.")
    print("1. Google 스프레드시트에서 대량 발송 (기본 스프레드시트)")
    print("2. 다른 Google 스프레드시트에서 대량 발송")
    print("3. 테스트 이메일 발송")

    choice = input("선택하세요 (1, 2 또는 3): ")

    if choice == "1":
        print(f"기본 스프레드시트 ID: {DEFAULT_SHEET_ID} 사용")
        send_instructor_emails(DEFAULT_SHEET_ID)
    elif choice == "2":
        sheet_id = input("Google 스프레드시트 ID를 입력하세요: ")
        send_instructor_emails(sheet_id)
    elif choice == "3":
        send_test_email()
    else:
        print("잘못된 선택입니다.")