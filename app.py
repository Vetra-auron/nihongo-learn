import streamlit as st
import os
import sys

# 경로 설정
sys.path.insert(0, os.path.dirname(__file__))

from database.init_db import init_database, load_initial_data, check_attendance_today
from utils.quiz_generator import get_statistics, get_today_words

# 페이지 설정
st.set_page_config(
    page_title="일본어 학습 - にほんご",
    page_icon="🇯🇵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 데이터베이스 초기화
@st.cache_resource
def setup_database():
    init_database()
    load_initial_data()
    return True

setup_database()

# 출석 체크
check_attendance_today()

# 커스텀 CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #E53935;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        color: white;
        text-align: center;
        margin: 0.5rem;
    }
    .stat-number {
        font-size: 2.5rem;
        font-weight: bold;
    }
    .stat-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    .today-word {
        background: #fff3e0;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border-left: 4px solid #ff9800;
    }
    .japanese-text {
        font-size: 1.5rem;
        font-weight: bold;
        color: #333;
    }
    .korean-text {
        color: #666;
    }
</style>
""", unsafe_allow_html=True)

# 헤더
st.markdown('<div class="main-header">🇯🇵 일본어 학습</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">매일 조금씩, 꾸준히 일본어 실력을 키워보세요!</div>', unsafe_allow_html=True)

# 통계 가져오기
stats = get_statistics()

# 대시보드 통계 카드
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-number">🔥 {stats['streak']}</div>
        <div class="stat-label">연속 학습일</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    user_added = stats.get('user_added_words', 0)
    st.markdown(f"""
    <div class="stat-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
        <div class="stat-number">📚 {stats['learned_words']}</div>
        <div class="stat-label">학습한 단어 (내 단어 {user_added})</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="stat-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
        <div class="stat-number">📝 {stats['quiz_count']}</div>
        <div class="stat-label">완료한 퀴즈</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="stat-card" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
        <div class="stat-number">⭐ {stats['avg_score']}%</div>
        <div class="stat-label">평균 점수</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# 오늘의 학습
st.subheader("📖 오늘의 학습 단어")

today_words = get_today_words(5)

if today_words:
    cols = st.columns(len(today_words))
    for idx, word in enumerate(today_words):
        with cols[idx]:
            st.markdown(f"""
            <div class="today-word">
                <div class="japanese-text">{word['japanese']}</div>
                <div class="korean-text">{word['korean']}</div>
            </div>
            """, unsafe_allow_html=True)
else:
    st.info("오늘의 학습 단어가 없습니다.")

st.markdown("---")

# 빠른 메뉴
st.subheader("🚀 빠른 시작")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    ### 📚 단어장
    일본어 단어를 체계적으로 학습하세요.
    예문과 암기 팁으로 쉽게 외울 수 있어요!
    """)
    if st.button("단어장 열기", key="btn_vocab", use_container_width=True):
        st.switch_page("pages/1_📚_단어장.py")

with col2:
    st.markdown("""
    ### 🎯 퀴즈
    배운 내용을 테스트해보세요.
    1단계: 오늘 학습 / 2단계: 전체 복습
    """)
    if st.button("퀴즈 시작", key="btn_quiz", use_container_width=True):
        st.switch_page("pages/3_🎯_퀴즈.py")

with col3:
    st.markdown("""
    ### 📊 성과
    학습 진행 상황을 확인하세요.
    출석, 점수, 취약점 분석까지!
    """)
    if st.button("성과 보기", key="btn_stats", use_container_width=True):
        st.switch_page("pages/5_📊_성과.py")

# 사이드바
with st.sidebar:
    st.markdown("### 📅 학습 정보")
    st.markdown(f"**총 학습일:** {stats['total_study_days']}일")
    st.markdown(f"**학습 진도:** {stats['learned_words']}/{stats['total_words']} 단어")
    
    user_added = stats.get('user_added_words', 0)
    if user_added > 0:
        st.markdown(f"**내가 추가한 단어:** {user_added}개")
    
    progress = stats['learned_words'] / stats['total_words'] if stats['total_words'] > 0 else 0
    st.progress(progress)
    
    st.markdown("---")
    st.markdown("### 💡 오늘의 팁")
    tips = [
        "매일 5개 단어만 외워도 1년이면 1,825개!",
        "예문과 함께 외우면 기억에 오래 남아요.",
        "틀린 문제는 오답노트에서 복습하세요.",
        "꾸준함이 가장 중요해요! 🔥",
        "한자의 뜻을 알면 단어 암기가 쉬워져요.",
        "나만의 단어를 추가해서 학습해보세요!"
    ]
    import random
    st.info(random.choice(tips))
