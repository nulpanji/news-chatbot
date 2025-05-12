import streamlit as st
import requests
from deep_translator import GoogleTranslator
import datetime

NEWSAPI_KEY = "3b875f9e3b684d0398ca52bebdbf7a9b"

# 주요 토픽/키워드별로 뉴스 수집
HOT_TOPICS = [
    ("테슬라", "tesla"),
    ("엔비디아", "nvidia"),
    ("비트코인", "bitcoin"),
    ("XRP(리플)", "xrp"),
    ("도지코인", "dogecoin"),
    ("경제", "economy"),
    ("사회", "society"),
    ("국제", "international"),
    ("스포츠", "sports"),
    ("자동차", "automobile"),
    ("모터사이클", "motorcycle")
]

# 각 토픽별로 뉴스 가져오기 (인기순)
def fetch_topic_news(topic_en, max_articles=15):
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": topic_en,
        "from": (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=7)).strftime("%Y-%m-%d"),
        "sortBy": "popularity",
        "language": "en",
        "pageSize": max_articles,
        "apiKey": NEWSAPI_KEY
    }
    try:
        res = requests.get(url, params=params, timeout=10)
        data = res.json()
        if data.get("status") == "ok":
            return data.get("articles", [])
        else:
            print(f"[{topic_en}] API error: {data}")
    except Exception as e:
        print(f"[{topic_en}] 오류: {e}")
    return []
                    })
        except Exception as e:
            print(f"[{country}] 오류: {e}")

    # 2. NewsAPI의 Everything에서 인기 토픽
    topics = [
        "global economy", "international politics", "technology innovation",
        "climate change", "health crisis", "breaking news", "major sports"
    ]
    for topic in topics:
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": topic,
            "from": from_date,
            "sortBy": "popularity",
            "language": "en",
            "pageSize": 5,
            "apiKey": NEWSAPI_KEY
        }
        try:
            res = requests.get(url, params=params, timeout=10)
            data = res.json()
            if data.get("status") == "ok":
                for art in data.get("articles", []):
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

    # 중복 제거 (제목 기반)
    unique_articles = []
    seen_titles = set()
    for article in all_articles:
        title = article.get("title", "") or ""
        normalized_title = title.lower().strip()
        if normalized_title and normalized_title not in seen_titles:
            seen_titles.add(normalized_title)
            unique_articles.append(article)

    # 최신순 정렬
    unique_articles.sort(key=lambda x: x["pub_date"], reverse=True)
    return unique_articles[:30]

# --- Streamlit UI ---
st.set_page_config(page_title="🌏 글로벌 뉴스 리더", layout="wide")
st.title("🌏 글로벌 핫뉴스 리더")
st.write("지난 7일간 세계적으로 가장 인기있는 뉴스 30개를 보여줍니다.")

lang_option = st.radio("기사 언어 선택", ["영어 원본", "한국어 번역"], horizontal=True)
translate_to_ko = lang_option == "한국어 번역"

news_list = fetch_hot_news()

if not news_list:
    st.info("최근 7일 이내 주요 뉴스가 없습니다.")
else:
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
        st.caption(f"{art['source']} | {art['pub_date']}")