import streamlit as st
import requests
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# .env 또는 Streamlit Secrets에서 API 키 조회
EXCHANGERATE_API_KEY = os.getenv("EXCHANGERATE_API_KEY") or st.secrets.get("EXCHANGERATE_API_KEY")

# 페이지 기본 설정
st.set_page_config(
    page_title="PIXEL EXCHANGE",
    page_icon="🪙",
    layout="centered"
)

# 픽셀 아트 스타일 커스텀 CSS 주입
st.markdown("""
<style>
    /* 레트로 픽셀 폰트 (둥근모 + Press Start 2P) */
    @import url('https://cdn.jsdelivr.net/gh/neodgm/neodgm-webfont@latest/style.css');
    @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');

    html, body, [class*="css"], .stApp {
        font-family: 'DungGeunMo', 'Press Start 2P', monospace !important;
        background-color: #f7a8c4; /* 이미지 특유의 파스텔 핑크 */
    }

    /* 메인 윈도우 창 프레임 */
    .pixel-window {
        background-color: #79ebd2; /* 민트 에메랄드 */
        border: 4px solid #000;
        box-shadow: 6px 6px 0px #000;
        padding: 0;
        margin-bottom: 25px;
    }

    .pixel-window-header {
        background-color: #5c3596; /* 레트로 퍼플 헤더 */
        color: #ffffff;
        padding: 8px 12px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 4px solid #000;
        font-size: 14px;
    }

    .pixel-window-body {
        padding: 20px;
        background-color: #8cebd9;
    }

    /* 스트림릿 기본 인풋 및 셀렉트박스 각진 픽셀화 */
    div[data-baseweb="input"], div[data-baseweb="select"] {
        border: 3px solid #000 !important;
        border-radius: 0px !important;
        box-shadow: 4px 4px 0px #000 !important;
        background-color: #fff !important;
    }

    /* 버튼 픽셀화 및 클릭 효과 */
    div.stButton > button {
        border: 3px solid #000 !important;
        border-radius: 0px !important;
        box-shadow: 4px 4px 0px #000 !important;
        background-color: #ffde59 !important; /* 노란색 레트로 버튼 */
        color: #000 !important;
        font-family: 'DungGeunMo', monospace !important;
        font-size: 16px !important;
        font-weight: bold !important;
        width: 100%;
        padding: 10px 0px !important;
        transition: 0.1s;
    }

    div.stButton > button:active {
        box-shadow: 0px 0px 0px #000 !important;
        transform: translate(4px, 4px);
    }

    /* 결과 출력 박스 */
    .result-box {
        background-color: #fff5ea;
        border: 4px solid #000;
        box-shadow: 5px 5px 0px #000;
        padding: 15px;
        text-align: center;
        margin-top: 15px;
    }
</style>
""", unsafe_allow_html=True)

# 환율 데이터 수신 및 캐싱 (1시간 유지)
@st.cache_data(ttl=3600)
def get_exchange_rates(base_currency, api_key):
    # ExchangeRate-API 규격 URL
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/{base_currency}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

# 지원 통화 목록 (주요 통화)
CURRENCIES = ["USD", "EUR", "KRW", "JPY", "GBP", "AUD", "CAD", "CNY"]

# 헤더 UI 렌더링
st.markdown("""
<div class="pixel-window">
    <div class="pixel-window-header">
        <span>EXCHANGE_CALC.EXE</span>
        <span>[?] [-] [X]</span>
    </div>
    <div class="pixel-window-body">
        <h2 style="margin: 0; text-align: center; color: #000; font-size: 22px;">★ 환율 계산기 ★</h2>
    </div>
</div>
""", unsafe_allow_html=True)

# 입력 폼
col1, col2 = st.columns(2)
with col1:
    base_curr = st.selectbox("보유 통화", CURRENCIES, index=0)
with col2:
    target_curr = st.selectbox("환전할 통화", CURRENCIES, index=2)

amount = st.number_input("변환할 금액", min_value=0.0, value=1.0, step=1.0)

# 계산 실행
if st.button("CALCULATE ▶"):
    if not EXCHANGERATE_API_KEY:
        st.error("API 키가 설정되지 않았습니다. .env 파일에 EXCHANGERATE_API_KEY를 입력해주세요.")
    elif base_curr == target_curr:
        st.markdown(f"""
        <div class="result-box">
            <h3 style="color: #000; margin: 0;">동일한 통화입니다: {amount:,.2f} {base_curr}</h3>
        </div>
        """, unsafe_allow_html=True)
    else:
        with st.spinner("FETCHING DATA..."):
            data = get_exchange_rates(base_curr, EXCHANGERATE_API_KEY)
            
        if data and data.get("result") == "success" and target_curr in data.get("conversion_rates", {}):
            rates = data["conversion_rates"]
            rate = rates[target_curr]
            converted = amount * rate
            
            st.markdown(f"""
            <div class="result-box">
                <p style="color: #666; margin: 0; font-size: 13px;">1 {base_curr} = {rate:,.4f} {target_curr}</p>
                <h2 style="color: #000; margin: 10px 0 0 0;">{converted:,.2f} {target_curr}</h2>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.error("환율 데이터를 불러오는데 실패했습니다. API 키가 유효한지 확인해주세요.")