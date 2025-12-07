import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.quiz_generator import get_all_words, get_today_words, mark_word_learned

st.set_page_config(page_title="단어장 - 일본어 학습", page_icon="📚", layout="wide")

st.title("📚 단어장")

# 탭 생성
tab1, tab2, tab3 = st.tabs(["📖 오늘의 단어", "📚 전체 단어", "🔍 검색"])

# 오늘의 단어 탭
with tab1:
    st.subheader("오늘 학습할 단어")
    
    today_words = get_today_words(5)
    
    if not today_words:
        st.info("오늘 학습할 단어가 없습니다.")
    else:
        for idx, word in enumerate(today_words):
            with st.expander(f"**{word['japanese']}** - {word['korean']}", expanded=(idx == 0)):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"### {word['japanese']}")
                    if word.get('hiragana'):
                        st.markdown(f"**읽기:** {word['hiragana']}")
                    if word.get('kanji'):
                        st.markdown(f"**한자:** {word['kanji']}")
                    st.markdown(f"**뜻:** {word['korean']}")
                    st.markdown(f"**분류:** {word.get('category', '-')}")
                    st.markdown(f"**레벨:** {word.get('level', 'N5')}")
                
                with col2:
                    if word.get('memo_tip'):
                        st.info(f"💡 **암기 팁**\n\n{word['memo_tip']}")
                
                st.markdown("---")
                
                if word.get('example_sentence'):
                    st.markdown("**📝 예문**")
                    st.markdown(f"> {word['example_sentence']}")
                    if word.get('example_korean'):
                        st.markdown(f"> {word['example_korean']}")
                
                if st.button(f"✅ 학습 완료", key=f"learn_{word['id']}"):
                    mark_word_learned(word['id'])
                    st.success("학습 완료로 표시했습니다!")
                    st.rerun()

# 전체 단어 탭
with tab2:
    st.subheader("전체 단어 목록")
    
    all_words = get_all_words()
    
    # 필터
    col1, col2 = st.columns(2)
    with col1:
        categories = list(set(w.get('category', '기타') for w in all_words if w.get('category')))
        categories = ['전체'] + sorted(categories)
        selected_category = st.selectbox("카테고리", categories)
    
    with col2:
        levels = ['전체', 'N5', 'N4', 'N3', 'N2', 'N1']
        selected_level = st.selectbox("레벨", levels)
    
    # 필터 적용
    filtered_words = all_words
    if selected_category != '전체':
        filtered_words = [w for w in filtered_words if w.get('category') == selected_category]
    if selected_level != '전체':
        filtered_words = [w for w in filtered_words if w.get('level') == selected_level]
    
    st.markdown(f"**총 {len(filtered_words)}개의 단어**")
    
    # 페이지네이션
    items_per_page = 10
    total_pages = (len(filtered_words) - 1) // items_per_page + 1 if filtered_words else 1
    
    if 'vocab_page' not in st.session_state:
        st.session_state.vocab_page = 1
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("◀ 이전", disabled=st.session_state.vocab_page <= 1):
            st.session_state.vocab_page -= 1
            st.rerun()
    with col2:
        st.markdown(f"<center>{st.session_state.vocab_page} / {total_pages}</center>", unsafe_allow_html=True)
    with col3:
        if st.button("다음 ▶", disabled=st.session_state.vocab_page >= total_pages):
            st.session_state.vocab_page += 1
            st.rerun()
    
    # 단어 표시
    start_idx = (st.session_state.vocab_page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    page_words = filtered_words[start_idx:end_idx]
    
    for word in page_words:
        with st.expander(f"**{word['japanese']}** ({word.get('hiragana', '')}) - {word['korean']}"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                if word.get('kanji'):
                    st.markdown(f"**한자:** {word['kanji']}")
                st.markdown(f"**분류:** {word.get('category', '-')}")
                
                if word.get('example_sentence'):
                    st.markdown("**예문:**")
                    st.markdown(f"> {word['example_sentence']}")
                    if word.get('example_korean'):
                        st.markdown(f"> {word['example_korean']}")
            
            with col2:
                if word.get('memo_tip'):
                    st.info(f"💡 {word['memo_tip']}")

# 검색 탭
with tab3:
    st.subheader("단어 검색")
    
    search_query = st.text_input("검색어를 입력하세요 (일본어/한국어)")
    
    if search_query:
        all_words = get_all_words()
        results = [
            w for w in all_words 
            if search_query.lower() in w.get('japanese', '').lower()
            or search_query.lower() in w.get('korean', '').lower()
            or search_query.lower() in w.get('hiragana', '').lower()
        ]
        
        st.markdown(f"**{len(results)}개의 결과**")
        
        for word in results:
            with st.expander(f"**{word['japanese']}** - {word['korean']}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    if word.get('hiragana'):
                        st.markdown(f"**읽기:** {word['hiragana']}")
                    if word.get('kanji'):
                        st.markdown(f"**한자:** {word['kanji']}")
                    st.markdown(f"**분류:** {word.get('category', '-')}")
                    
                    if word.get('example_sentence'):
                        st.markdown("**예문:**")
                        st.markdown(f"> {word['example_sentence']}")
                        if word.get('example_korean'):
                            st.markdown(f"> {word['example_korean']}")
                
                with col2:
                    if word.get('memo_tip'):
                        st.info(f"💡 {word['memo_tip']}")
