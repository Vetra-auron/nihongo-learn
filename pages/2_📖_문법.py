import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.quiz_generator import get_all_grammars

st.set_page_config(page_title="문법 - 일본어 학습", page_icon="📖", layout="wide")

st.title("📖 문법")

# 문법 데이터 가져오기
all_grammars = get_all_grammars()

# 탭
tab1, tab2 = st.tabs(["📚 문법 목록", "🔍 검색"])

with tab1:
    st.subheader(f"N5 문법 ({len(all_grammars)}개)")
    
    for idx, grammar in enumerate(all_grammars):
        with st.expander(f"**{grammar['pattern']}** - {grammar['meaning']}", expanded=(idx == 0)):
            # 기본 정보
            st.markdown(f"### {grammar['pattern']}")
            st.markdown(f"**의미:** {grammar['meaning']}")
            
            if grammar.get('explanation'):
                st.markdown(f"**설명:** {grammar['explanation']}")
            
            if grammar.get('connection_rule'):
                st.info(f"📐 **접속 규칙**\n\n{grammar['connection_rule']}")
            
            st.markdown("---")
            
            # 예문
            if grammar.get('example_sentence'):
                st.markdown("**📝 예문**")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**일본어:** {grammar['example_sentence']}")
                with col2:
                    if grammar.get('example_korean'):
                        st.markdown(f"**한국어:** {grammar['example_korean']}")

with tab2:
    st.subheader("문법 검색")
    
    search_query = st.text_input("검색어를 입력하세요 (문법 패턴/의미)")
    
    if search_query:
        results = [
            g for g in all_grammars
            if search_query.lower() in g.get('pattern', '').lower()
            or search_query.lower() in g.get('meaning', '').lower()
            or search_query.lower() in g.get('explanation', '').lower()
        ]
        
        st.markdown(f"**{len(results)}개의 결과**")
        
        for grammar in results:
            with st.expander(f"**{grammar['pattern']}** - {grammar['meaning']}"):
                st.markdown(f"**설명:** {grammar.get('explanation', '-')}")
                
                if grammar.get('connection_rule'):
                    st.info(f"📐 {grammar['connection_rule']}")
                
                if grammar.get('example_sentence'):
                    st.markdown("**예문:**")
                    st.markdown(f"> {grammar['example_sentence']}")
                    if grammar.get('example_korean'):
                        st.markdown(f"> {grammar['example_korean']}")

# 사이드바에 문법 요약
with st.sidebar:
    st.markdown("### 📋 문법 요약")
    st.markdown("""
    **N5 주요 문법 카테고리:**
    
    1. **기본 문형**
       - ～です / ～ます
       - ～は～です
    
    2. **조사**
       - は, が, を, に, で, と
       - から～まで, も
    
    3. **동사 활용**
       - ～ている (진행)
       - ～たい (희망)
       - ～てください (부탁)
    
    4. **표현**
       - ～ましょう (권유)
       - ～てもいい (허가)
       - ～てはいけない (금지)
    """)
