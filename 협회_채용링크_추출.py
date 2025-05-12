import pandas as pd
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

file_path = r"C:\Users\LG\Documents\Windsurf\협회 List.xlsx"
output_path = r"C:\Users\LG\Documents\Windsurf\협회_채용결과.xlsx"

# 키워드 목록(필요시 추가/수정)
keywords = ['경력무관', '나이무관', '초보', '신입', '무관', '경력', '연령', '나이제한없음']

# 엑셀 파일 읽기
df = pd.read_excel(file_path)

results = []

for idx, row in df.iterrows():
    url = row['홈페이지 URL']
    company = row['협회명']
    no = row['No.'] if 'No.' in row else idx+1
    if not isinstance(url, str) or not url.startswith('http'):
        continue
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        found_any = False
        for a in soup.find_all('a', href=True):
            text = a.get_text()
            href = a['href']
            if href.startswith('javascript:'):
                continue
            if any(keyword in text for keyword in ['채용', '구인', '일자리', 'recruit', 'employment']):
                full_link = urljoin(url, href)
                # 채용공고 페이지에서 키워드 추출
                try:
                    job_resp = requests.get(full_link, timeout=10)
                    job_resp.raise_for_status()
                    job_soup = BeautifulSoup(job_resp.text, 'html.parser')
                    page_text = job_soup.get_text(separator=' ')
                    found_keywords = [kw for kw in keywords if kw in page_text]
                    found_keywords_str = ', '.join(found_keywords) if found_keywords else '없음'
                except Exception as e2:
                    found_keywords_str = f'[채용공고페이지 에러] {e2}'
                results.append({
                    'No.': no,
                    '협회명': company,
                    '홈페이지 URL': url,
                    '채용 관련 링크명': text.strip(),
                    '채용 관련 링크주소': full_link,
                    '채용공고 키워드': found_keywords_str
                })
                found_any = True
        if not found_any:
            results.append({
                'No.': no,
                '협회명': company,
                '홈페이지 URL': url,
                '채용 관련 링크명': '없음',
                '채용 관련 링크주소': '',
                '채용공고 키워드': ''
            })
    except Exception as e:
        results.append({
            'No.': no,
            '협회명': company,
            '홈페이지 URL': url,
            '채용 관련 링크명': f'[에러] {e}',
            '채용 관련 링크주소': '',
            '채용공고 키워드': ''
        })

result_df = pd.DataFrame(results)
result_df.to_excel(output_path, index=False)

print(f"결과가 엑셀 파일로 저장되었습니다: {output_path}")
