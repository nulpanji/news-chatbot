import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import streamlit as st
import feedparser
from googletrans import Translator

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

def fetch_and_translate_news(category, keyword=None, max_articles=5, translate_to_ko=False):
    articles = []
    feeds = RSS_FEEDS.get(category, [])
    for url in feeds:
        feed = feedparser.parse(url)
        for entry in feed.entries[:max_articles]:
            title = entry.title
            summary = entry.summary if 'summary' in entry else ''
            link = entry.link
            # 기사 언어 감지 (간단: 한국 언론사면 한글, 아니면 영어)
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
            # 키워드 필터
            if keyword:
                if keyword.lower() not in title_ko.lower() and keyword.lower() not in summary_ko.lower():
                    continue
            articles.append({
                'title': title_ko,
                'summary': summary_ko,
                'link': link,
                'source': feed.feed.title if 'title' in feed.feed else url
            })
    return articles

# Streamlit 웹챗봇 UI
st.title("🌏 실시간 뉴스 챗봇")
st.write("카테고리와(선택) 키워드를 입력하면 관련 뉴스를 한국어 또는 원본으로 요약해 드립니다.")

col1, col2 = st.columns([1,2])
category = col1.selectbox("카테고리", list(RSS_FEEDS.keys()))
keyword = col2.text_input("키워드(선택)", "")
lang_option = st.radio("기사 언어 선택", ["원본(영어/한국어)", "모든 기사 한국어로 번역"], horizontal=True)
translate_to_ko = lang_option == "모든 기사 한국어로 번역"

def fetch_and_translate_news(category, keyword=None, max_articles=20, translate_to_ko=False):
    articles = []
    feeds = RSS_FEEDS.get(category, [])
    for url in feeds:
        feed = feedparser.parse(url)
        for entry in feed.entries[:max_articles]:
            title = entry.title
            summary = entry.summary if 'summary' in entry else ''
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
                'source': feed.feed.title if 'title' in feed.feed else url
            })
    return articles

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
            st.caption(f"출처: {art['source']}")
            st.write("---")
