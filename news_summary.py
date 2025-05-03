import streamlit as st
import feedparser
from googletrans import Translator
import datetime
import re
import yfinance as yf
import requests
import re
import yfinance as yf
import requests

# 신뢰 언론사 RSS 피드 (글로벌 + 한국)
RSS_FEEDS = {
    '국제': [
        'http://feeds.bbci.co.uk/news/world/rss.xml',
        'http://feeds.reuters.com/Reuters/worldNews',
        'https://apnews.com/rss',
        'https://www.yna.co.kr/rss/all.do?site=001',  # 연합뉴스 국제 포함
    ],
    '경제': [
        'https://feeds.bbci.co.uk/news/business/rss.xml',
        'http://feeds.reuters.com/reuters/businessNews',
        'https://www.bloomberg.co.kr/feed/podcast/etf-report.xml',
        'https://www.hankyung.com/feed/news',
        'https://rss.donga.com/economy.xml',
    ],
    '사회': [
        'https://www.hani.co.kr/rss/',
        'https://rss.donga.com/society.xml',
        'https://www.chosun.com/arc/outboundfeeds/rss/category/national/?outputType=xml',
    ],
    '스포츠': [
        'http://www.yonhapnewstv.co.kr/browse/feed/14',
        'https://www.chosun.com/arc/outboundfeeds/rss/category/sports/?outputType=xml',
        'https://sports.news.naver.com/rss/index.nhn',
    ]
}

translator = Translator()

# HOT 뉴스 키워드 확장 (경제/테크 포함)
HOT_NEWS_KEYWORDS = [
    "전쟁", "지진", "태풍", "쓰나미", "폭발", "긴급", "속보", "breaking", "alert", "emergency", "disaster", "전투", "공습", "폭우", "홍수",
    "테슬라", "tesla", "엔비디아", "nvidia", "코인", "비트코인", "bitcoin", "이더리움", "ethereum", "xrp", "리플", "주식", "환율", "금리", "증시", "stock", "market", "fed", "연준"
]

# 실시간 HOT 뉴스 추출
def fetch_hot_news():
    articles = []
    now = datetime.datetime.utcnow()
    two_days_ago = now - datetime.timedelta(days=2)
    for cat in RSS_FEEDS:
        for url in RSS_FEEDS[cat]:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                pub_date = None
                for date_key in ['published_parsed', 'updated_parsed']:
                    if date_key in entry and entry[date_key]:
                        pub_date = datetime.datetime(*entry[date_key][:6])
                        break
                if not pub_date or pub_date < two_days_ago:
                    continue
                title = entry.title
                if 'content' in entry and entry.content:
                    summary = entry.content[0].value
                elif 'summary' in entry:
                    summary = entry.summary
                else:
                    summary = ''
                texts = [title, summary]
                found = False
                for kw in HOT_NEWS_KEYWORDS:
                    for txt in texts:
                        if re.search(kw, txt, re.IGNORECASE):
                            found = True
                            break
                    if found:
                        break
                if not found:
                    continue
                articles.append({
                    'title': title,
                    'summary': summary,
                    'link': entry.link,
                    'source': feed.feed.title if 'title' in feed.feed else url,
                    'pub_date': pub_date
                })
    articles.sort(key=lambda x: x['pub_date'], reverse=True)
    return articles[:10]  # 상위 10건만

# 실시간 주식 시세 (Yahoo Finance)
def fetch_stock_price(symbol):
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="1d")
        if not data.empty:
            price = data['Close'].iloc[-1]
            return f"{price:,.2f}"
        else:
            return "N/A"
    except Exception:
        return "N/A"

# 실시간 코인 시세 (CoinGecko)
def fetch_crypto_price(symbol):
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=krw,usd"
        res = requests.get(url, timeout=5)
        data = res.json()
        price_krw = data[symbol]['krw']
        price_usd = data[symbol]['usd']
        return f"₩{price_krw:,} / ${price_usd:,}"
    except Exception:
        return "N/A"

# 실시간 환율 (USD/KRW, EUR/KRW, Yahoo Finance)
def fetch_fx_rate(pair):
    try:
        ticker = yf.Ticker(pair)
        data = ticker.history(period="1d")
        if not data.empty:
            rate = data['Close'].iloc[-1]
            return f"{rate:,.2f}"
        else:
            return "N/A"
    except Exception:
        return "N/A"

# 실시간 날씨 (OpenWeatherMap)
OPENWEATHER_API_KEY = "b28b5663f60a009761ddeb6059a824fe"
def fetch_weather(city="Seoul"):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric&lang=kr"
        res = requests.get(url, timeout=5)
        data = res.json()
        temp = data['main']['temp']
        desc = data['weather'][0]['description']
        return f"{city}: {temp}°C, {desc}"
    except Exception:
        return f"{city}: N/A"

def fetch_and_translate_news(keyword=None, translate_to_ko=False):
    articles = []
    now = datetime.datetime.utcnow()
    one_month_ago = now - datetime.timedelta(days=31)
    all_feeds = sum(RSS_FEEDS.values(), [])
    for url in all_feeds:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            # 날짜 파싱
            pub_date = None
            for date_key in ['published_parsed', 'updated_parsed']:
                if date_key in entry and entry[date_key]:
                    pub_date = datetime.datetime(*entry[date_key][:6])
                    break
            if not pub_date:
                continue
            # 한 달 이내만
            if pub_date < one_month_ago:
                continue
            title = entry.title
            # content 우선, 없으면 summary
            if 'content' in entry and entry.content:
                summary = entry.content[0].value
            elif 'summary' in entry:
                summary = entry.summary
            else:
                summary = ''
            link = entry.link
            is_korean_news = any(domain in url for domain in [
                'yna.co.kr', 'hani.co.kr', 'donga.com', 'chosun.com', 'naver.com', 'hankyung.com'
            ])
            if translate_to_ko or not is_korean_news:
                try:
                    title_ko = translator.translate(title, dest='ko').text if not is_korean_news else title
                except Exception:
                    title_ko = title
                try:
                    summary_ko = translator.translate(summary, dest='ko').text if summary and not is_korean_news else summary
                except Exception:
                    summary_ko = summary
            else:
                title_ko = title
                summary_ko = summary
            # 키워드 필터 (원문+번역 모두 포함)
            if keyword:
                keyword_lower = keyword.lower()
                if (keyword_lower not in title.lower() and
                    keyword_lower not in summary.lower() and
                    keyword_lower not in title_ko.lower() and
                    keyword_lower not in summary_ko.lower()):
                    continue
            articles.append({
                'title': title_ko,
                'summary': summary_ko,
                'link': link,
                'source': feed.feed.title if 'title' in feed.feed else url,
                'pub_date': pub_date
            })
    # 최신순 정렬 (맨 위가 최신)
    articles.sort(key=lambda x: x['pub_date'], reverse=True)
    return articles

# Streamlit 웹챗봇 UI
# ---- UI ----
st.set_page_config(page_title="실시간 뉴스 챗봇", layout="wide")
st.markdown("""
<style>
    .main {max-width: 700px; margin: auto;}
    @media (max-width: 600px) {
        .main {max-width: 100vw; padding: 0 8px;}
    }
</style>
<div class="main">
""", unsafe_allow_html=True)

st.title("🌏 실시간 뉴스 챗봇")
st.write("카테고리와(선택) 키워드를 입력하면 관련 뉴스를 한국어 또는 원본으로 요약해 드립니다.")

# --- HOT 뉴스, 시세, 환율, 날씨 위젯 ---
hot_news = fetch_hot_news()
with st.expander("🔥 실시간 속보/Hot News (최근 2일)", expanded=True):
    if not hot_news:
        st.info("최근 2일 이내 속보/핫뉴스가 없습니다.")
    else:
        for i, art in enumerate(hot_news, 1):
            st.markdown(f"**{i}. [{art['title']}]({art['link']})**")
            if art['summary']:
                st.write(f"요약: {art['summary']}")
            st.caption(f"출처: {art['source']} | 날짜: {art['pub_date'].strftime('%Y-%m-%d %H:%M')}")
            st.write("---")

st.subheader(":chart_with_upwards_trend: 실시간 시세/환율/날씨")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("테슬라(TSLA)", fetch_stock_price("TSLA"))
    st.metric("엔비디아(NVDA)", fetch_stock_price("NVDA"))
with col2:
    st.metric("삼성전자(005930.KS)", fetch_stock_price("005930.KS"))
    st.metric("비트코인(BTC)", fetch_crypto_price("bitcoin"))
with col3:
    st.metric("이더리움(ETH)", fetch_crypto_price("ethereum"))
    st.metric("XRP", fetch_crypto_price("ripple"))
with col4:
    st.metric("USD/KRW", fetch_fx_rate("USDKRW=X"))
    st.metric("EUR/KRW", fetch_fx_rate("EURKRW=X"))
    st.metric("서울 날씨", fetch_weather("Seoul"))

# ---- 뉴스 검색 UI ----
keyword = st.text_input("키워드로 뉴스 검색 (카테고리 구분 없음)", "")
lang_option = st.radio("기사 언어 선택", ["원본(영어/한국어)", "모든 기사 한국어로 번역"], horizontal=True)
translate_to_ko = lang_option == "모든 기사 한국어로 번역"

if st.button("뉴스 찾기"):
    with st.spinner("뉴스를 불러오는 중..."):
        articles = fetch_and_translate_news(keyword.strip(), translate_to_ko=translate_to_ko)
    if not articles:
        st.warning("관련 뉴스가 없습니다.")
    else:
        for i, art in enumerate(articles, 1):
            st.markdown(f"**{i}. [{art['title']}]({art['link']})**")
            if art['summary']:
                st.write(f"요약: {art['summary']}")
            st.caption(f"출처: {art['source']} | 날짜: {art['pub_date'].strftime('%Y-%m-%d %H:%M')}")
            st.write("---")

st.markdown("</div>", unsafe_allow_html=True)

# ---- 도메인 주소 유지 안내 ----
# 가비아 프레임 포워딩 사용 시 주소창에 www.nulpanji.com 유지 가능(단, 일부 브라우저에서 차단될 수 있음)
# 완벽한 커스텀 도메인 연결을 원하면 Netlify/Vercel 등으로 마이그레이션 필요
