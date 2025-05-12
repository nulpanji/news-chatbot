import streamlit as st
import requests
from deep_translator import GoogleTranslator
import datetime
import os

def fetch_hot_news():
    print("[DEBUG] 🔄 fetch_hot_news() 시작됨")
    NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
    print(f"[DEBUG] NEWSAPI_KEY: {NEWSAPI_KEY}")
    countries = ['us', 'kr', 'jp']
    all_articles = []

    # 1. 국가별 헤드라인 (Top Headlines)
    for country in countries:
        url = "https://newsapi.org/v2/top-headlines"
        params = {
            "country": country,
            "pageSize": 3,
            "apiKey": NEWSAPI_KEY
        }
        try:
            res = requests.get(url, params=params, timeout=10)
            data = res.json()
            print(f"[DEBUG] {country} API 응답: {data}")
            if data.get("status") == "ok":
                articles = data.get("articles", [])
                print(f"[{country.upper()} 헤드라인] {len(articles)}개 기사 가져옴")
                for art in articles:
                    title = art.get("title", "")
                    summary = art.get("description", "")
                    link = art.get("url", "")
                    source = art.get("source", {}).get("name", "")
                    pub_date = art.get("publishedAt", "")[:16].replace("T", " ")
                    all_articles.append({
                        "title": title,
                        "summary": summary,
                        "link": link,
                        "source": source,
                        "pub_date": pub_date,
                        "country": country.upper(),
                        "type": "headline"
                    })
        except Exception as e:
            print(f"[{country}] 오류: {e}")

    print(f"[DEBUG] 🌍 수집된 전체 기사 수 (중복 포함): {len(all_articles)}")

    # 2. 인기 주제 기반 Everything 검색
    url = "https://newsapi.org/v2/everything"
    from_date = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=3)).strftime("%Y-%m-%d")
    topics = [
        "global economy", "international politics", "technology innovation"
    ]
    for topic in topics:
        params = {
            "q": topic,
            "from": from_date,
            "sortBy": "popularity",
            "language": "en",
            "pageSize": 2,
            "apiKey": NEWSAPI_KEY
        }
        try:
            res = requests.get(url, params=params, timeout=10)
            data = res.json()
            print(f"[DEBUG] {topic} API 응답: {data}")
            if data.get("status") == "ok":
                articles = data.get("articles", [])
                print(f"[{topic}] {len(articles)}개 인기 기사 가져옴")
                for art in articles:
                    title = art.get("title", "")
                    summary = art.get("description", "")
                    link = art.get("url", "")
                    source = art.get("source", {}).get("name", "")
                    pub_date = art.get("publishedAt", "")[:16].replace("T", " ")
                    all_articles.append({
                        "title": title,
                        "summary": summary,
                        "link": link,
                        "source": source,
                        "pub_date": pub_date,
                        "topic": topic,
                        "type": "popular"
                    })
        except Exception as e:
            print(f"[{topic}] 오류: {e}")

    # 3. 중복 제거
    seen_titles = set()
    unique_articles = []
    for article in all_articles:
        title = (article.get("title") or "").lower().strip()
        if title and title not in seen_titles:
            seen_titles.add(title)
            unique_articles.append(article)

    print(f"[DEBUG] ✅ 중복 제거 후 기사 수: {len(unique_articles)}")

    # 4. 최신순 정렬
    headlines = [a for a in unique_articles if a.get("type") == "headline"]
    populars = [a for a in unique_articles if a.get("type") == "popular"]
    headlines.sort(key=lambda x: x["pub_date"], reverse=True)
    populars.sort(key=lambda x: x["pub_date"], reverse=True)

    return (headlines + populars)[:30]

# --- Streamlit UI ---
# Render 호환: PORT 환경변수로 포트 바인딩 (필수)
if "PORT" in os.environ:
    import sys
    port = int(os.environ["PORT"])
    sys.argv += ["run", sys.argv[0], "--server.port", str(port)]

st.set_page_config(page_title="🌏 글로벌 뉴스 리더", layout="wide")
st.title("🌏 글로벌 핫뉴스 리더")
st.write("지난 7일간 세계적으로 가장 인기있는 뉴스 30개를 보여줍니다.")

lang_option = st.radio("기사 언어 선택", ["영어 원본", "한국어 번역"], horizontal=True)
translate_to_ko = lang_option == "한국어 번역"

news_list = fetch_hot_news()

if not news_list:
    # 더미 데이터로 UI 정상 동작 확인
    news_list = [{
        "title": "Streamlit 앱은 정상 작동 중입니다!",
        "summary": "API에서 뉴스가 오지 않을 때 이 문구가 뜹니다.",
        "link": "https://newsapi.org",
        "source": "NewsAPI 테스트",
        "pub_date": "2025-05-13"
    }]

for i, art in enumerate(news_list, 1):
    title = art['title']
    summary = art['summary']
    if translate_to_ko:
        try:
            title = GoogleTranslator(source='auto', target='ko').translate(title) if title else title
        except Exception:
            pass
        try:
            summary = GoogleTranslator(source='auto', target='ko').translate(summary) if summary else summary
        except Exception:
            pass
    st.markdown(f"**{i}. [{title}]({art['link']})**")
    if summary:
        st.write(summary[:150] + ("..." if len(summary) > 150 else ""))
    st.caption(f"{art.get('source', '')} | {art.get('pub_date', '')}")