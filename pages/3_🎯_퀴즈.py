import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.quiz_generator import (
    generate_full_quiz, save_quiz_result, save_wrong_answer,
    get_today_words, get_learned_words
)
from database.init_db import update_attendance

st.set_page_config(page_title="퀴즈 - 일본어 학습", page_icon="🎯", layout="wide")

st.title("🎯 퀴즈")

# 세션 상태 초기화
if 'quiz_started' not in st.session_state:
    st.session_state.quiz_started = False
if 'quiz_questions' not in st.session_state:
    st.session_state.quiz_questions = []
if 'current_question' not in st.session_state:
    st.session_state.current_question = 0
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'answers' not in st.session_state:
    st.session_state.answers = []
if 'quiz_type' not in st.session_state:
    st.session_state.quiz_type = 'today'
if 'show_result' not in st.session_state:
    st.session_state.show_result = False

def reset_quiz():
    st.session_state.quiz_started = False
    st.session_state.quiz_questions = []
    st.session_state.current_question = 0
    st.session_state.score = 0
    st.session_state.answers = []
    st.session_state.show_result = False

# 퀴즈 시작 전
if not st.session_state.quiz_started:
    st.markdown("""
    ### 📋 퀴즈 유형을 선택하세요
    
    퀴즈는 **20문제**로 구성되어 있습니다.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        #### 1️⃣ 오늘의 학습 퀴즈
        - 오늘 학습한 단어 위주
        - 새로운 내용 점검에 적합
        - 난이도: ⭐⭐
        """)
        if st.button("1단계 시작", key="start_today", use_container_width=True):
            st.session_state.quiz_type = 'today'
            st.session_state.quiz_questions = generate_full_quiz('today', 14, 6)
            if st.session_state.quiz_questions:
                st.session_state.quiz_started = True
                st.rerun()
            else:
                st.error("퀴즈를 생성할 수 없습니다. 먼저 단어를 학습해주세요!")
    
    with col2:
        st.markdown("""
        #### 2️⃣ 종합 복습 퀴즈
        - 지금까지 배운 모든 범위
        - 실력 점검에 적합
        - 난이도: ⭐⭐⭐
        """)
        if st.button("2단계 시작", key="start_all", use_container_width=True):
            st.session_state.quiz_type = 'all'
            st.session_state.quiz_questions = generate_full_quiz('all', 14, 6)
            if st.session_state.quiz_questions:
                st.session_state.quiz_started = True
                st.rerun()
            else:
                st.error("퀴즈를 생성할 수 없습니다. 데이터가 부족합니다.")

# 퀴즈 진행 중
elif st.session_state.quiz_started and not st.session_state.show_result:
    questions = st.session_state.quiz_questions
    current_idx = st.session_state.current_question
    
    if current_idx < len(questions):
        question = questions[current_idx]
        
        # 진행 상황
        progress = (current_idx) / len(questions)
        st.progress(progress)
        st.markdown(f"**문제 {current_idx + 1} / {len(questions)}**")
        
        # 문제 표시
        st.markdown("---")
        
        question_type_label = "📚 단어" if question['type'] == 'word' else "📖 문법"
        st.markdown(f"### {question_type_label}")
        st.markdown(f"## {question['question']}")
        
        # 보기
        st.markdown("---")
        
        selected = None
        cols = st.columns(2)
        
        for idx, option in enumerate(question['options']):
            col_idx = idx % 2
            with cols[col_idx]:
                if st.button(
                    f"{idx + 1}. {option}",
                    key=f"option_{current_idx}_{idx}",
                    use_container_width=True
                ):
                    selected = option
                    
                    # 정답 체크
                    is_correct = selected == question['correct_answer']
                    
                    st.session_state.answers.append({
                        'question': question,
                        'selected': selected,
                        'correct': is_correct
                    })
                    
                    if is_correct:
                        st.session_state.score += 1
                    else:
                        # 오답 기록
                        content_type = question['type']
                        content_id = question.get('word_id') or question.get('grammar_id')
                        if content_id:
                            save_wrong_answer(
                                question.get('question_type', 'general'),
                                content_type,
                                content_id
                            )
                    
                    # 다음 문제로
                    st.session_state.current_question += 1
                    
                    if st.session_state.current_question >= len(questions):
                        st.session_state.show_result = True
                    
                    st.rerun()
        
        # 힌트 버튼
        if question.get('hint'):
            with st.expander("💡 힌트 보기"):
                st.info(question['hint'])
        
        # 포기 버튼
        st.markdown("---")
        if st.button("🚪 퀴즈 그만두기"):
            reset_quiz()
            st.rerun()

# 결과 화면
elif st.session_state.show_result:
    questions = st.session_state.quiz_questions
    score = st.session_state.score
    total = len(questions)
    percentage = (score / total) * 100 if total > 0 else 0
    
    # 결과 저장
    save_quiz_result(
        st.session_state.quiz_type,
        score,
        total,
        {'answers': [{'correct': a['correct']} for a in st.session_state.answers]}
    )
    update_attendance(quiz_taken=1)
    
    # 결과 표시
    st.markdown("---")
    st.markdown("## 🎉 퀴즈 완료!")
    
    # 점수에 따른 메시지
    if percentage >= 90:
        st.balloons()
        grade = "🏆 완벽해요!"
        color = "#4CAF50"
    elif percentage >= 70:
        grade = "👍 잘했어요!"
        color = "#2196F3"
    elif percentage >= 50:
        grade = "💪 조금 더 힘내요!"
        color = "#FF9800"
    else:
        grade = "📚 복습이 필요해요"
        color = "#f44336"
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div style="text-align: center; padding: 2rem; background: {color}; border-radius: 1rem; color: white;">
            <h1>{score} / {total}</h1>
            <p>정답 수</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="text-align: center; padding: 2rem; background: {color}; border-radius: 1rem; color: white;">
            <h1>{percentage:.0f}%</h1>
            <p>정답률</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="text-align: center; padding: 2rem; background: {color}; border-radius: 1rem; color: white;">
            <h1>{grade}</h1>
            <p>평가</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 오답 확인
    wrong_answers = [a for a in st.session_state.answers if not a['correct']]
    
    if wrong_answers:
        st.subheader(f"❌ 틀린 문제 ({len(wrong_answers)}개)")
        
        for idx, answer in enumerate(wrong_answers):
            q = answer['question']
            with st.expander(f"문제 {idx + 1}: {q['question']}"):
                st.error(f"**내 답:** {answer['selected']}")
                st.success(f"**정답:** {q['correct_answer']}")
                if q.get('hint'):
                    st.info(f"💡 **팁:** {q['hint']}")
    
    # 다시 시작 버튼
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 다시 도전하기", use_container_width=True):
            reset_quiz()
            st.rerun()
    
    with col2:
        if st.button("📝 오답노트 보기", use_container_width=True):
            st.switch_page("pages/4_📝_오답노트.py")

# 사이드바
with st.sidebar:
    st.markdown("### 📊 현재 퀴즈 정보")
    
    if st.session_state.quiz_started:
        st.markdown(f"**유형:** {'오늘의 학습' if st.session_state.quiz_type == 'today' else '종합 복습'}")
        st.markdown(f"**진행:** {st.session_state.current_question} / {len(st.session_state.quiz_questions)}")
        st.markdown(f"**현재 점수:** {st.session_state.score}")
    else:
        st.info("퀴즈를 시작해주세요!")
    
    st.markdown("---")
    st.markdown("### 💡 퀴즈 팁")
    st.markdown("""
    - 모르면 힌트를 활용하세요
    - 틀린 문제는 오답노트에서 복습
    - 꾸준히 퀴즈를 풀면 실력 UP!
    """)
