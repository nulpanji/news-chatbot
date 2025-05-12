import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = [
    '[https://www.googleapis.com/auth/drive.readonly',](https://www.googleapis.com/auth/drive.readonly',)
    '[https://www.googleapis.com/auth/spreadsheets'](https://www.googleapis.com/auth/spreadsheets')
]

def get_credentials():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def main():
    creds = get_credentials()
    drive_service = build('drive', 'v3', credentials=creds)
    sheets_service = build('sheets', 'v4', credentials=creds)

    # 예시: 구글 드라이브에서 스프레드시트 파일 목록 출력
    folder_id = '1mxwOu7RCmQ1eRqNkW1xjb0af-hzxSbk7'  # 실제 폴더 ID로 변경 가능
    query = f"'{folder_id}' in parents and mimeType='application/vnd.google-apps.spreadsheet'"
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get('files', [])

    print("Google Drive 내 스프레드시트 파일 목록:")
    for file in files:
        print(f"- {file['name']} (ID: {file['id']})")

if __name__ == '__main__':
    main()
