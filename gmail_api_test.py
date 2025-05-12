from __future__ import print_function
import os.path
import base64
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def gmail_send_message(to, subject, body):
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'gmail auto sending json file.json', SCOPES)  # 실제 파일명으로!
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)
    message = MIMEText(body, 'html')
    message['to'] = to
    message['subject'] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    message = {'raw': raw}
    send_message = service.users().messages().send(userId="me", body=message).execute()
    print(f"Message Id: {send_message['id']}")
    print("이메일이 성공적으로 발송되었습니다.")

if __name__ == '__main__':
    to = input("받는 사람 이메일 주소: ")
    subject = "Gmail API 테스트 메일"
    body = "<h3>이것은 Gmail API를 이용한 자동 발송 테스트입니다.</h3>"
    gmail_send_message(to, subject, body)
