import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.quiz_generator import get_wrong_answers, resolve_wrong_answer

st.set_page_config(page_title="오답노트 - 일본어 학습", page_icon="📝", layout="wide")

st.title("📝 오답노트")

st.markdown("""
틀린 문제들을 모아서 복습해보세요. 
취약한 부분을 집중적으로 학습하면 실력이 빠르게 향상됩니다!
""")

# 오답 데이터 가져오기
wrong_data = get_wrong_answers()
word_wrongs = wrong_data['words']
grammar_wrongs = wrong_data['grammars']

total_wrongs = len(word_wrongs) + len(grammar_wrongs)

if total_wrongs == 0:
    st.success("🎉 축하합니다! 현재 오답이 없습니다!")
    st.markdown("퀴즈를 풀고 틀린 문제가 있으면 여기에 기록됩니다.")
else:
    st.warning(f"📚 총 {total_wrongs}개의 복습이 필요한 항목이 있습니다.")

# 탭 생성
tab1, tab2, tab3 = st.tabs([
    f"📚 단어 오답 ({len(word_wrongs)})", 
    f"📖 문법 오답 ({len(grammar_wrongs)})",
    "📊 분석"
])

# 단어 오답 탭
with tab1:
    if not word_wrongs:
        st.info("단어 오답이 없습니다! 👍")
    else:
        st.subheader("틀린 단어 목록")
        st.markdown("*틀린 횟수가 많은 순서대로 정렬됩니다.*")
        
        for wrong in word_wrongs:
            wrong_count = wrong['wrong_count']
            urgency = "🔴" if wrong_count >= 3 else "🟡" if wrong_count >= 2 else "🟢"
            
            with st.expander(f"{urgency} **{wrong['japanese']}** - {wrong['korean']} (틀린 횟수: {wrong_count}회)"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"### {wrong['japanese']}")
                    if wrong.get('hiragana'):
                        st.markdown(f"**읽기:** {wrong['hiragana']}")
                    st.markdown(f"**뜻:** {wrong['korean']}")
                    
                    if wrong.get('memo_tip'):
                        st.info(f"💡 **암기 팁:** {wrong['memo_tip']}")
                
                with col2:
                    st.markdown(f"**틀린 횟수:** {wrong_count}회")
                    st.markdown(f"**마지막 오답:** {wrong['last_wrong_at'][:10]}")
                    
                    if st.button("✅ 이해했어요!", key=f"resolve_word_{wrong['id']}"):
                        resolve_wrong_answer(wrong['id'])
                        st.success("복습 완료!")
                        st.rerun()

# 문법 오답 탭
with tab2:
    if not grammar_wrongs:
        st.info("문법 오답이 없습니다! 👍")
    else:
        st.subheader("틀린 문법 목록")
        
        for wrong in grammar_wrongs:
            wrong_count = wrong['wrong_count']
            urgency = "🔴" if wrong_count >= 3 else "🟡" if wrong_count >= 2 else "🟢"
            
            with st.expander(f"{urgency} **{wrong['pattern']}** - {wrong['meaning']} (틀린 횟수: {wrong_count}회)"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"### {wrong['pattern']}")
                    st.markdown(f"**의미:** {wrong['meaning']}")
                    
                    if wrong.get('explanation'):
                        st.info(f"📖 **설명:** {wrong['explanation']}")
                
                with col2:
                    st.markdown(f"**틀린 횟수:** {wrong_count}회")
                    
                    if st.button("✅ 이해했어요!", key=f"resolve_grammar_{wrong['id']}"):
                        resolve_wrong_answer(wrong['id'])
                        st.success("복습 완료!")
                        st.rerun()

# 분석 탭
with tab3:
    st.subheader("📊 오답 분석")
    
    if total_wrongs == 0:
        st.info("분석할 오답 데이터가 없습니다.")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 유형별 분포")
            
            import pandas as pd
            
            data = {
                '유형': ['단어', '문법'],
                '개수': [len(word_wrongs), len(grammar_wrongs)]
            }
            df = pd.DataFrame(data)
            st.bar_chart(df.set_index('유형'))
        
        with col2:
            st.markdown("### 취약 분야")
            
            if len(word_wrongs) > len(grammar_wrongs):
                st.error("📚 **단어** 학습에 더 집중이 필요합니다!")
                st.markdown("""
                **추천 학습법:**
                - 예문과 함께 단어 암기
                - 암기 팁 활용하기
                - 매일 5개씩 복습
                """)
            elif len(grammar_wrongs) > len(word_wrongs):
                st.error("📖 **문법** 학습에 더 집중이 필요합니다!")
                st.markdown("""
                **추천 학습법:**
                - 접속 규칙 꼼꼼히 확인
                - 예문을 직접 만들어보기
                - 유사 문법 비교 학습
                """)
            else:
                st.warning("단어와 문법 모두 고르게 복습이 필요합니다.")
        
        # 자주 틀리는 항목
        st.markdown("---")
        st.markdown("### 🔴 자주 틀리는 항목 (3회 이상)")
        
        frequent_wrongs = [w for w in word_wrongs if w['wrong_count'] >= 3]
        frequent_wrongs += [g for g in grammar_wrongs if g['wrong_count'] >= 3]
        
        if frequent_wrongs:
            for item in frequent_wrongs:
                if 'japanese' in item:
                    st.markdown(f"- **{item['japanese']}** ({item['korean']}) - {item['wrong_count']}회")
                else:
                    st.markdown(f"- **{item['pattern']}** ({item['meaning']}) - {item['wrong_count']}회")
        else:
            st.success("3회 이상 틀린 항목이 없습니다!")

# 사이드바
with st.sidebar:
    st.markdown("### 📋 오답노트 요약")
    st.markdown(f"**총 오답 수:** {total_wrongs}개")
    st.markdown(f"- 단어: {len(word_wrongs)}개")
    st.markdown(f"- 문법: {len(grammar_wrongs)}개")
    
    st.markdown("---")
    st.markdown("### 💡 복습 팁")
    st.markdown("""
    1. 틀린 횟수가 많은 것부터 복습
    2. 이해했으면 '이해했어요' 클릭
    3. 정기적으로 오답노트 확인
    4. 같은 유형을 자주 틀리면 해당 분야 집중 학습
    """)
