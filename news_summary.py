import streamlit as st
import requests
from deep_translator import GoogleTranslator
import datetime

NEWSAPI_KEY = "f2f31ac43bcd4f7aab46adf98f73b8dd"

# 지난 7일간의 글로벌 주요 뉴스(속보/핫/인기) 30개 반환
def fetch_hot_news():
    countries = ['us', 'gb', 'jp', 'kr', 'sg', 'de', 'fr', 'ca', 'au']
    all_articles = []
    now = datetime.datetime.now(datetime.timezone.utc)
    from_date = (now - datetime.timedelta(days=7)).strftime("%Y-%m-%d")

    # 1. NewsAPI의 Top Headlines (국가별)
    for country in countries:
        url = "https://newsapi.org/v2/top-headlines"
        params = {
            "country": country,
            "pageSize": 10,
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
                        "country": country.upper(),
                        "type": "headline"
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

# NewsAPI로 키워드 뉴스 검색 (최대 100개, 언어: 영어/한국어/다국어)
def fetch_newsapi_articles(keyword, translate_to_ko=False):
    from deep_translator import GoogleTranslator
    try:
        keyword_en = GoogleTranslator(source='ko', target='en').translate(keyword)
    except Exception:
        keyword_en = keyword
    results = []
    for use_kw in [keyword, keyword_en]:
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": use_kw,
            "from": (datetime.datetime.utcnow() - datetime.timedelta(days=30)).strftime("%Y-%m-%d"),
            "sortBy": "publishedAt",
            "language": "all",  # ko/en/all 모두 시도
            "pageSize": 100,
            "apiKey": NEWSAPI_KEY,
        }
        res = requests.get(url, params=params, timeout=10)
        data = res.json()
        print(f"[NewsAPI] '{use_kw}' totalResults:", data.get("totalResults"), "/ articles:", len(data.get("articles", [])))
        keywords = [k.strip() for k in keyword.split() if k.strip()]
        for art in data.get("articles", []):
            title = art["title"] or ""
            summary = art["description"] or ""
            link = art["url"]
            source = art["source"]["name"]
            pub_date = art["publishedAt"][:16].replace("T", " ")
            text = (title + " " + summary).lower()
            # OR 검색: 하나라도 포함
            if any(k.lower() in text for k in keywords):
                if translate_to_ko:
                    try:
                        title_ko = GoogleTranslator(source='auto', target='ko').translate(title) if title else title
                    except Exception:
                        title_ko = title
                    try:
                        summary_ko = GoogleTranslator(source='auto', target='ko').translate(summary) if summary else summary
                    except Exception:
                        summary_ko = summary
                else:
                    title_ko = title
                    summary_ko = summary
                results.append({
                    "title": title_ko,
                    "summary": summary_ko,
                    "link": link,
                    "source": source,
                    "pub_date": pub_date
                })
    return results, len(results)

# 실시간 HOT 뉴스 추출 - 선진국 중심 인기 뉴스 기반
def fetch_hot_news():
    import datetime
    # 주요 선진국 목록
    countries = ['us', 'gb', 'jp', 'kr', 'sg', 'de', 'fr', 'ca', 'au']
    all_articles = []
    
    # 1. NewsAPI의 Top Headlines 사용 (국가별 헤드라인)
    for country in countries:
        url = "https://newsapi.org/v2/top-headlines"
        params = {
            "country": country,
            "pageSize": 10,  # 국가당 최대 10개
            "apiKey": NEWSAPI_KEY
        }
        try:
            res = requests.get(url, params=params, timeout=10)
            data = res.json()
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
    
    # 2. NewsAPI의 Everything 에서 인기도 기반 검색
    url = "https://newsapi.org/v2/everything"
    from_date = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=3)).strftime("%Y-%m-%d")
    # 주요 토픽 키워드
    topics = [
        "global economy", "international politics", "technology innovation", 
        "climate change", "health crisis", "breaking news", "major sports"
    ]
    
    for topic in topics:
        params = {
            "q": topic,
            "from": from_date,
            "sortBy": "popularity",  # 인기도 기반 정렬
            "language": "en",
            "pageSize": 5,  # 토픽당 5개
            "apiKey": NEWSAPI_KEY
        }
        try:
            res = requests.get(url, params=params, timeout=10)
            data = res.json()
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
    
    # 3. 중복 제거 (제목 기반)
    unique_articles = []
    seen_titles = set()
    
    for article in all_articles:
        # 제목 정리 (공백 제거, 소문자화)
        # 제목이 None이면 빈 문자열로 처리
        title = article.get("title", "")
        if title is None:
            title = ""
        normalized_title = title.lower().strip()
        if normalized_title and normalized_title not in seen_titles:
            seen_titles.add(normalized_title)
            unique_articles.append(article)
    
    print(f"[총계] 중복 제거 후 {len(unique_articles)}개 기사")
    
    # 4. 최신순 + 인기도 기준 혼합 정렬
    # 헤드라인은 우선순위, 나머지는 최신순
    headlines = [a for a in unique_articles if a.get("type") == "headline"]
    popular_articles = [a for a in unique_articles if a.get("type") == "popular"]
    
    # 최신순 정렬
    headlines.sort(key=lambda x: x["pub_date"], reverse=True)
    popular_articles.sort(key=lambda x: x["pub_date"], reverse=True)
    
    # 헤드라인 먼저, 나머지 인기기사 나중
    final_articles = headlines + popular_articles
    
    # 최대 30개만 반환
    return final_articles[:30]


# 실시간 주식 시세 (Yahoo Finance)


def fetch_and_translate_news(keyword=None, translate_to_ko=False):
    articles = fetch_newsapi_articles(keyword, translate_to_ko=translate_to_ko)
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
            if translate_to_ko:
                try:
                    title_ko = translator.translate(title, dest='ko').text
                except Exception:
                    title_ko = title
                try:
                    summary_ko = translator.translate(summary, dest='ko').text if summary else summary
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

import openai
import os

# OpenAI API 키 설정
def get_openai_api_key():
    # 시크릿에서 키 가져오기 시도
    api_key = None
    try:
        if "OPENAI_API_KEY" in st.secrets:
            api_key = st.secrets["OPENAI_API_KEY"]
            print("Streamlit secrets에서 API 키를 가져왔습니다.")
    except Exception as e:
        print(f"Streamlit secrets 오류: {e}")
    
    # 환경 변수에서 키 가져오기 시도
    if not api_key:
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            print("환경 변수에서 API 키를 가져왔습니다.")
    
    # 키가 없으면 상수 값 사용 (실제 프로덕션에서는 사용하지 마세요!)
    if not api_key:
        # 임시 테스트용 API 키 (실제 프로덕션에서는 사용하지 마세요!)
        api_key = "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"
        print("기본 API 키를 사용합니다. 실제 프로덕션에서는 변경해주세요.")
    
    return api_key

# 시스템 프롬프트 정의 - 뉴스 챗봇의 역할과 행동 방식 정의
def get_system_prompt():
    return """당신은 실시간 뉴스 챗봇입니다. 사용자의 질문을 이해하고 관련 뉴스를 제공하는 역할을 합니다.

다음 규칙을 따르세요:
1. 사용자가 특정 키워드나 주제에 대한 뉴스를 묻는다면, 그 주제에 대한 뉴스를 요약해서 제공하세요.
2. 이전 대화의 맥락을 유지하세요. 예를 들어 사용자가 '더 자세히 알려줘' 라고 하면 이전 주제에 대해 더 자세한 정보를 제공하세요.
3. 사용자가 새로운 주제나 키워드를 언급하면, 그에 대한 새로운 뉴스를 찾아 제공하세요.
4. 사용자가 이전 대화에서 언급되지 않은 새로운 질문을 하면, 새로운 주제로 인식하고 그에 맞는 뉴스를 찾아 제공하세요.
5. 사용자가 뉴스가 아닌 일반적인 질문을 하면, 일반적인 정보를 제공하면서 뉴스 관련 질문을 하도록 유도하세요.
"""

# 대화 맥락을 처리하는 함수
def analyze_conversation_context(messages):
    # 맥락이 없으면 기본값 반환
    if len(messages) < 2:
        return None, None
    
    # 이전 대화에서 키워드 추출
    last_user_messages = [msg["content"] for msg in messages if msg["role"] == "user"][-3:]
    last_assistant_messages = [msg["content"] for msg in messages if msg["role"] == "assistant"][-3:]
    
    # 이전 대화 내용을 기반으로 현재 주제 추정
    context_messages = [
        {"role": "system", "content": "사용자와의 이전 대화를 분석하여 현재 대화의 주제와 키워드를 추출하세요. JSON 형태로 출력하세요: {\"main_topic\": \"주제\", \"keywords\": [\"키워드1\", \"키워드2\"]}"}
    ]
    
    # 이전 대화 내용 추가
    for user_msg, assistant_msg in zip(last_user_messages, last_assistant_messages):
        if user_msg and assistant_msg:
            context_messages.append({"role": "user", "content": user_msg})
            context_messages.append({"role": "assistant", "content": assistant_msg})
    
    # 현재 사용자 메시지 추가
    context_messages.append({"role": "user", "content": messages[-1]["content"]})
    
    try:
        # GPT를 사용하여 맥락 분석 (최신 API 버전)
        from openai import OpenAI
        client = OpenAI(api_key=get_openai_api_key())
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=context_messages,
            temperature=0.3,
            max_tokens=150
        )
        context_analysis = response.choices[0].message.content
        
        # JSON 파싱
        import json
        import re
        
        # JSON 형태로 추출
        json_match = re.search(r'\{.*\}', context_analysis, re.DOTALL)
        if json_match:
            context_data = json.loads(json_match.group(0))
            main_topic = context_data.get("main_topic")
            keywords = context_data.get("keywords", [])
            return main_topic, keywords
    except Exception as e:
        print(f"[Context Analysis] 오류: {e}")
    
    # 오류 발생 시 기본값 반환
    return None, None

# GPT를 통한 뉴스 요약 및 응답 생성
def ask_gpt(messages, news_articles=None):
    from openai import OpenAI
    
    # OpenAI 클라이언트 생성 (최신 API 버전)
    client = OpenAI(api_key=get_openai_api_key())
    
    # 시스템 프롬프트 추가
    gpt_messages = [
        {"role": "system", "content": get_system_prompt()}
    ]
    
    # 이전 대화 내용 추가
    for msg in messages:
        gpt_messages.append(msg)
    
    # 뉴스 기사 정보 추가
    if news_articles:
        news_context = """다음은 사용자의 질문과 관련된 최신 뉴스 기사들입니다. 이 내용을 바탕으로 사용자의 질문에 대해 정보를 제공하세요:\n\n"""
        
        for i, art in enumerate(news_articles[:5], 1):
            news_context += f"{i}. 제목: {art['title']}\n"
            if art['summary']:
                from bs4 import BeautifulSoup
                clean_summary = BeautifulSoup(art['summary'], "html.parser").get_text()
                news_context += f"   요약: {clean_summary[:200]}...\n"
            news_context += f"   출처: {art['source']} | 날짜: {art['pub_date']}\n\n"
        
        gpt_messages.append({"role": "system", "content": news_context})
    
    # 추가 지침 제공
    gpt_messages.append({"role": "system", "content": """
    사용자의 질문에 대한 답변을 작성하세요. 다음 규칙을 따르세요:
    1. 뉴스 기사의 정보를 바탕으로 사용자의 질문에 응답하세요.
    2. 자연스럽고 친절한 톤으로 응답하세요.
    3. 맥락에 따라 이전 대화를 참조하여 응답하세요.
    4. 만약 뉴스 기사가 없는 경우, 사용자에게 다른 키워드나 주제를 제안하세요.
    5. 만약 사용자가 더 자세한 정보나 추가 정보를 요청하면, 이전 기사의 내용을 바탕으로 더 자세히 설명하세요.
    """})
    
    # GPT 응답 생성 (최신 API 버전)
    try:
        # API 키 로그 추가 (개발용)
        api_key = get_openai_api_key()
        print(f"API 키 사용 중: {api_key[:5]}...{api_key[-4:] if api_key else 'None'}")
        
        # 클라이언트 재생성
        client = OpenAI(api_key=api_key)
        
        # API 호출
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=gpt_messages,
            temperature=0.7,
            max_tokens=1024
        )
        
        # 응답 추출
        if hasattr(response.choices[0], 'message') and hasattr(response.choices[0].message, 'content'):
            return response.choices[0].message.content
        else:
            print(f"OpenAI API 응답 구조 오류: {response}")
            return "죄송합니다. API 응답 형식이 올바르지 않습니다. 다시 시도해주세요."
    except openai.APIError as e:
        print(f"OpenAI API 오류: {e}")
        return f"죄송합니다. OpenAI API 오류가 발생했습니다: {str(e)[:100]}. 다시 시도해주세요."
    except openai.APIConnectionError as e:
        print(f"OpenAI API 연결 오류: {e}")
        return "죄송합니다. API 서버에 연결할 수 없습니다. 인터넷 연결을 확인하고 다시 시도해주세요."
    except openai.RateLimitError as e:
        print(f"OpenAI API 요율 제한 오류: {e}")
        return "죄송합니다. API 요청 한도를 초과했습니다. 잠시 후에 다시 시도해주세요."
    except openai.AuthenticationError as e:
        print(f"OpenAI API 인증 오류: {e}")
        return "죄송합니다. API 키 인증에 문제가 있습니다. 관리자에게 문의해주세요."
    except Exception as e:
        print(f"OpenAI API 기타 오류: {type(e).__name__}: {e}")
        return f"죄송합니다. 응답을 생성하는 중 오류가 발생했습니다: {type(e).__name__}. 다시 시도해주세요."

if submitted and user_input:
    # 사용자 메시지 추가
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # 대화 맥락 분석
    main_topic, keywords = None, []
    if len(st.session_state.messages) > 1:
        main_topic, keywords = analyze_conversation_context(st.session_state.messages)
    
    # 맥락이 없거나 새로운 주제인 경우 현재 입력을 기반으로 검색
    search_query = user_input
    
    # 맥락이 있고 현재 입력이 짧은 추가 질문이면 이전 주제 활용
    if main_topic and len(user_input.strip().split()) <= 5 and not any(kw.lower() in user_input.lower() for kw in ['테슬라', '삼성', '애플', '국제', '경제', '정치', '스포츠', '연예', '코로나', '전쟁', '기후']):
        follow_up_keywords = ["더", "자세히", "구체적으로", "어떤", "무엇", "언제", "어디서", "왜", "어떻게", "또", "추가로", "다른", "다음"]
        if any(kw in user_input.lower() for kw in follow_up_keywords) and keywords:
            # 후속 질문으로 판단되면 이전 키워드 활용
            search_query = main_topic if main_topic else " ".join(keywords[:2])
            print(f"[맥락 분석] 후속 질문 감지: '{user_input}' -> 검색어: '{search_query}'")
    
    # 뉴스 검색 실행
    news_articles, total_news = fetch_gnews_articles(search_query, translate_to_ko=translate_to_ko, lang="ko" if translate_to_ko else "en", max_articles=10)
    
    # GNews에서 결과가 없으면 NewsAPI도 시도
    if not news_articles:
        news_articles2, total_news2 = fetch_newsapi_articles(search_query, translate_to_ko=translate_to_ko)
        news_articles += news_articles2
    
    # 응답 생성 및 표시
    with st.chat_message("assistant"):
        if not news_articles:
            # 뉴스가 없는 경우 GPT만 사용하여 응답 생성
            gpt_reply = ask_gpt(st.session_state.messages)
            st.markdown(gpt_reply)
        else:
            # 뉴스 기사 표시
            for i, art in enumerate(news_articles[:5], 1):
                st.markdown(f"**{i}. [{art['title']}]({art['link']})**")
                if art['summary']:
                    from bs4 import BeautifulSoup
                    clean_summary = BeautifulSoup(art['summary'], "html.parser").get_text()
                    st.write(clean_summary[:150] + ("..." if len(clean_summary) > 150 else ""))
                st.caption(f"{art['source']} | {art['pub_date']}")
            
            # GPT를 통한 지능적 응답 생성
            gpt_reply = ask_gpt(st.session_state.messages, news_articles)
            st.markdown(f"\n\n**해석 및 요약:**\n{gpt_reply}")
    
    # 응답 메시지 저장
    st.session_state.messages.append({"role": "assistant", "content": gpt_reply})
    
    # UI 새로고침
    st.rerun()
