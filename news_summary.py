import streamlit as st
import feedparser
from googletrans import Translator
import datetime

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

def fetch_and_translate_news(category, keyword=None, translate_to_ko=False):
    articles = []
    feeds = RSS_FEEDS.get(category, [])
    now = datetime.datetime.utcnow()
    one_month_ago = now - datetime.timedelta(days=31)
    for url in feeds:
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
st.title("🌏 실시간 뉴스 챗봇")
st.write("카테고리와(선택) 키워드를 입력하면 관련 뉴스를 한국어 또는 원본으로 요약해 드립니다.")

col1, col2 = st.columns([1,2])
category = col1.selectbox("카테고리", list(RSS_FEEDS.keys()))
keyword = col2.text_input("키워드(선택)", "")
lang_option = st.radio("기사 언어 선택", ["원본(영어/한국어)", "모든 기사 한국어로 번역"], horizontal=True)
translate_to_ko = lang_option == "모든 기사 한국어로 번역"

if st.button("뉴스 찾기"):
    with st.spinner("뉴스를 불러오는 중..."):
        articles = fetch_and_translate_news(category, keyword.strip(), translate_to_ko=translate_to_ko)
    if not articles:
        st.warning("관련 뉴스가 없습니다.")
    else:
        for i, art in enumerate(articles, 1):
            st.markdown(f"**{i}. [{art['title']}]({art['link']})**")
            if art['summary']:
                st.write(f"요약: {art['summary']}")
            st.caption(f"출처: {art['source']} | 날짜: {art['pub_date'].strftime('%Y-%m-%d %H:%M')}")
            st.write("---")
