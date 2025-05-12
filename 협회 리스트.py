import pandas as pd
import requests
from bs4 import BeautifulSoup

# 엑셀 파일 경로
file_path = r"C:\Users\LG\Documents\Windsurf\협회 List.xlsx"

# 엑셀 파일 읽기
df = pd.read_excel(file_path)

# 홈페이지 URL 컬럼에서 주소만 추출 (결측치 제거)
urls = df['홈페이지 URL'].dropna().unique()

for url in urls:
    if not isinstance(url, str) or not url.startswith('http'):
        continue  # 잘못된 URL은 건너뜀
    try:
        print(f"접속 중: {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # "채용", "구인", "일자리" 등 키워드가 포함된 링크 찾기
        found = False
        for a in soup.find_all('a', href=True):
            text = a.get_text()
            if any(keyword in text for keyword in ['채용', '구인', '일자리', 'recruit', 'employment']):
                print(f"  - 채용 관련 링크: {text.strip()} ({a['href']})")
                found = True
        if not found:
            print("  - 채용 관련 링크를 찾지 못했습니다.")
        print("-" * 40)
    except Exception as e:
        print(f"  [에러] {url}: {e}")
