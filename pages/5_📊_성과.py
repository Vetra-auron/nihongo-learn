import streamlit as st
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.quiz_generator import (
    get_statistics, get_recent_quiz_results, get_attendance_history
)

st.set_page_config(page_title="성과 - 일본어 학습", page_icon="📊", layout="wide")

st.title("📊 학습 성과")

# 통계 가져오기
stats = get_statistics()
recent_quizzes = get_recent_quiz_results(10)
attendance = get_attendance_history(30)

# 상단 요약 카드
st.subheader("🏆 학습 현황")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="🔥 연속 학습일",
        value=f"{stats['streak']}일",
        delta="계속 유지하세요!" if stats['streak'] > 0 else None
    )

with col2:
    st.metric(
        label="📚 학습한 단어",
        value=f"{stats['learned_words']}개",
        delta=f"전체의 {stats['learned_words']*100//stats['total_words'] if stats['total_words'] > 0 else 0}%"
    )

with col3:
    st.metric(
        label="📝 완료한 퀴즈",
        value=f"{stats['quiz_count']}회"
    )

with col4:
    st.metric(
        label="⭐ 평균 점수",
        value=f"{stats['avg_score']}%",
        delta=f"최고: {stats['best_score']}%"
    )

st.markdown("---")

# 탭 생성
tab1, tab2, tab3 = st.tabs(["📅 출석 현황", "📈 퀴즈 기록", "🎯 목표 달성"])

# 출석 현황 탭
with tab1:
    st.subheader("📅 출석 캘린더")
    
    if not attendance:
        st.info("아직 출석 기록이 없습니다. 오늘부터 시작해보세요!")
    else:
        # 최근 30일 캘린더 표시
        import pandas as pd
        
        today = datetime.now().date()
        
        # 캘린더 데이터 준비
        attendance_dates = {a['date'] for a in attendance}
        
        # 주간 캘린더 표시 (최근 4주)
        st.markdown("**최근 4주 출석 현황**")
        
        weeks = []
        for week in range(4):
            week_start = today - timedelta(days=today.weekday() + 7 * week)
            week_data = []
            for day in range(7):
                d = week_start + timedelta(days=day)
                date_str = d.isoformat()
                if date_str in attendance_dates:
                    week_data.append("✅")
                elif d > today:
                    week_data.append("⬜")
                else:
                    week_data.append("❌")
            weeks.append(week_data)
        
        # 요일 헤더
        days = ['월', '화', '수', '목', '금', '토', '일']
        
        # 테이블 형태로 표시
        df = pd.DataFrame(weeks[::-1], columns=days)
        df.index = [f'{4-i}주 전' if i < 3 else '이번 주' for i in range(4)]
        st.dataframe(df, use_container_width=True)
        
        # 출석 통계
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"**총 학습일:** {len(attendance)}일")
        
        with col2:
            total_words = sum(a.get('words_learned', 0) for a in attendance)
            st.markdown(f"**총 학습 단어:** {total_words}개")
        
        with col3:
            total_quizzes = sum(a.get('quiz_taken', 0) for a in attendance)
            st.markdown(f"**총 퀴즈 수:** {total_quizzes}회")

# 퀴즈 기록 탭
with tab2:
    st.subheader("📈 퀴즈 성적 추이")
    
    if not recent_quizzes:
        st.info("아직 퀴즈 기록이 없습니다. 퀴즈를 풀어보세요!")
    else:
        import pandas as pd
        
        # 퀴즈 데이터 준비
        quiz_data = []
        for q in recent_quizzes:
            score_pct = (q['score'] / q['total_questions']) * 100 if q['total_questions'] > 0 else 0
            quiz_data.append({
                '날짜': q['completed_at'][:10],
                '유형': '오늘의 학습' if q['quiz_type'] == 'today' else '종합 복습',
                '점수': f"{q['score']}/{q['total_questions']}",
                '정답률': f"{score_pct:.0f}%",
                '정답률_수치': score_pct
            })
        
        df = pd.DataFrame(quiz_data)
        
        # 그래프
        if len(df) > 1:
            st.line_chart(df.set_index('날짜')['정답률_수치'])
        
        # 테이블
        st.markdown("**최근 퀴즈 기록**")
        display_df = df[['날짜', '유형', '점수', '정답률']].copy()
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        # 통계 요약
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            avg = df['정답률_수치'].mean()
            st.metric("평균 정답률", f"{avg:.1f}%")
        
        with col2:
            best = df['정답률_수치'].max()
            st.metric("최고 점수", f"{best:.0f}%")
        
        with col3:
            recent_avg = df['정답률_수치'].head(5).mean()
            st.metric("최근 5회 평균", f"{recent_avg:.1f}%")

# 목표 달성 탭
with tab3:
    st.subheader("🎯 학습 목표")
    
    # 목표 설정
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📚 단어 마스터")
        word_progress = stats['learned_words'] / stats['total_words'] if stats['total_words'] > 0 else 0
        st.progress(word_progress)
        st.markdown(f"**{stats['learned_words']} / {stats['total_words']}** 단어 학습 완료")
        
        # 마일스톤
        milestones = [10, 25, 50, 75, 100]
        for m in milestones:
            target = int(stats['total_words'] * m / 100)
            if stats['learned_words'] >= target:
                st.markdown(f"✅ {m}% 달성 ({target}단어)")
            else:
                st.markdown(f"⬜ {m}% ({target}단어까지 {target - stats['learned_words']}개 남음)")
    
    with col2:
        st.markdown("### 🔥 연속 출석")
        streak = stats['streak']
        
        # 출석 배지
        badges = [
            (3, "🌱 새싹", "3일 연속"),
            (7, "🌿 성장", "7일 연속"),
            (14, "🌳 꾸준함", "2주 연속"),
            (30, "🏆 달인", "30일 연속"),
            (100, "👑 마스터", "100일 연속")
        ]
        
        for days, badge, desc in badges:
            if streak >= days:
                st.markdown(f"✅ {badge} - {desc}")
            else:
                st.markdown(f"⬜ {badge} - {desc} ({days - streak}일 남음)")
    
    st.markdown("---")
    
    # 퀴즈 마스터
    st.markdown("### 📝 퀴즈 마스터")
    
    col1, col2, col3 = st.columns(3)
    
    quiz_count = stats['quiz_count']
    
    with col1:
        if quiz_count >= 1:
            st.success("✅ 첫 퀴즈 완료!")
        else:
            st.info("⬜ 첫 퀴즈에 도전하세요!")
    
    with col2:
        if quiz_count >= 10:
            st.success("✅ 10회 퀴즈 달성!")
        else:
            st.info(f"⬜ 10회 퀴즈 ({quiz_count}/10)")
    
    with col3:
        if stats['best_score'] >= 100:
            st.success("✅ 만점 달성!")
        else:
            st.info(f"⬜ 만점 도전! (최고: {stats['best_score']}%)")

# 사이드바
with st.sidebar:
    st.markdown("### 📋 오늘의 목표")
    
    # 오늘 목표 체크리스트
    goals = [
        ("📚 단어 5개 학습", True if stats['streak'] > 0 else False),
        ("📝 퀴즈 1회 완료", stats['quiz_count'] > 0),
        ("📖 문법 복습", False),
        ("✍️ 예문 작성", False)
    ]
    
    for goal, completed in goals:
        if completed:
            st.markdown(f"✅ ~~{goal}~~")
        else:
            st.markdown(f"⬜ {goal}")
    
    st.markdown("---")
    st.markdown("### 💪 동기부여")
    
    motivations = [
        "千里の道も一歩から\n(천 리 길도 한 걸음부터)",
        "継続は力なり\n(계속은 힘이다)",
        "塵も積もれば山となる\n(티끌 모아 태산)",
        "石の上にも三年\n(돌 위에도 3년)"
    ]
    
    import random
    st.info(random.choice(motivations))
