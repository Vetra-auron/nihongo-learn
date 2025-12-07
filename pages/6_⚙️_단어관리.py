import streamlit as st
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database.init_db import get_connection

st.set_page_config(page_title="단어 관리 - 일본어 학습", page_icon="⚙️", layout="wide")

st.title("⚙️ 단어 관리")

st.markdown("""
나만의 단어를 추가하고 관리하세요!  
추가한 단어는 퀴즈와 학습에 **우선 반영**됩니다.
""")

# 탭 생성
tab1, tab2, tab3 = st.tabs(["📥 단어 추가", "📋 내 단어 목록", "📤 데이터 내보내기"])

# ===== 탭 1: 단어 추가 =====
with tab1:
    st.subheader("📥 새 단어 추가")
    
    # 입력 방식 선택
    input_method = st.radio(
        "입력 방식 선택",
        ["📝 폼으로 입력", "📄 JSON으로 입력"],
        horizontal=True
    )
    
    if input_method == "📝 폼으로 입력":
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            japanese = st.text_input("일본어 *", placeholder="例: たべる")
            hiragana = st.text_input("히라가나", placeholder="例: たべる")
            kanji = st.text_input("한자", placeholder="例: 食べる")
            korean = st.text_input("한국어 뜻 *", placeholder="例: 먹다")
        
        with col2:
            level = st.selectbox("레벨", ["N5", "N4", "N3", "N2", "N1"])
            category = st.selectbox(
                "카테고리",
                ["명사", "동사", "형용사", "부사", "대명사", "조사", "접속사", "숫자", "시간", "기타"]
            )
            example_sentence = st.text_input("예문 (일본어)", placeholder="例: ご飯を食べます。")
            example_korean = st.text_input("예문 (한국어)", placeholder="例: 밥을 먹습니다.")
        
        memo_tip = st.text_area("암기 팁", placeholder="例: 2그룹 동사, る를 빼고 활용")
        
        # 사용자 추가 단어 표시
        is_user_added = st.checkbox("내가 추가한 단어로 표시", value=True)
        
        if st.button("➕ 단어 추가", type="primary", use_container_width=True):
            if not japanese or not korean:
                st.error("일본어와 한국어 뜻은 필수입니다!")
            else:
                conn = get_connection()
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO words (japanese, hiragana, kanji, korean, level, category, 
                                      example_sentence, example_korean, memo_tip, is_user_added)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (japanese, hiragana, kanji, korean, level, category,
                      example_sentence, example_korean, memo_tip, 1 if is_user_added else 0))
                
                conn.commit()
                conn.close()
                
                st.success(f"✅ '{japanese}' 단어가 추가되었습니다!")
                st.balloons()
    
    else:  # JSON 입력
        st.markdown("---")
        st.markdown("""
        **JSON 형식으로 여러 단어를 한번에 추가**할 수 있습니다.
        
        아래 형식을 참고하세요:
        """)
        
        # JSON 예시
        example_json = '''[
    {
        "japanese": "あたらしい",
        "hiragana": "あたらしい",
        "kanji": "新しい",
        "korean": "새롭다",
        "level": "N5",
        "category": "형용사",
        "example_sentence": "新しい本を買いました。",
        "example_korean": "새 책을 샀습니다.",
        "memo_tip": "い형용사, 新 = 새로울 신"
    },
    {
        "japanese": "ふるい",
        "hiragana": "ふるい",
        "kanji": "古い",
        "korean": "오래되다, 낡다",
        "level": "N5",
        "category": "형용사",
        "example_sentence": "この建物は古いです。",
        "example_korean": "이 건물은 오래됐습니다.",
        "memo_tip": "い형용사, 古 = 옛 고"
    }
]'''
        
        with st.expander("📋 JSON 형식 예시 보기"):
            st.code(example_json, language="json")
        
        json_input = st.text_area(
            "JSON 입력",
            height=300,
            placeholder="위 형식대로 JSON을 입력하세요..."
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("✅ JSON 검증", use_container_width=True):
                if json_input.strip():
                    try:
                        data = json.loads(json_input)
                        if isinstance(data, list):
                            st.success(f"✅ 유효한 JSON입니다! ({len(data)}개 단어)")
                            for idx, word in enumerate(data[:3]):
                                st.info(f"{idx+1}. {word.get('japanese', '?')} - {word.get('korean', '?')}")
                            if len(data) > 3:
                                st.info(f"... 외 {len(data)-3}개")
                        elif isinstance(data, dict):
                            st.success("✅ 유효한 JSON입니다! (1개 단어)")
                            st.info(f"1. {data.get('japanese', '?')} - {data.get('korean', '?')}")
                        else:
                            st.error("배열 또는 객체 형태여야 합니다.")
                    except json.JSONDecodeError as e:
                        st.error(f"❌ JSON 형식 오류: {e}")
                else:
                    st.warning("JSON을 입력해주세요.")
        
        with col2:
            if st.button("📥 단어 추가", type="primary", use_container_width=True):
                if json_input.strip():
                    try:
                        data = json.loads(json_input)
                        
                        # 단일 객체면 리스트로 변환
                        if isinstance(data, dict):
                            data = [data]
                        
                        if not isinstance(data, list):
                            st.error("배열 또는 객체 형태여야 합니다.")
                        else:
                            conn = get_connection()
                            cursor = conn.cursor()
                            
                            added_count = 0
                            for word in data:
                                japanese = word.get('japanese', '')
                                korean = word.get('korean', '')
                                
                                if japanese and korean:
                                    cursor.execute('''
                                        INSERT INTO words (japanese, hiragana, kanji, korean, level, category,
                                                          example_sentence, example_korean, memo_tip, is_user_added)
                                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                                    ''', (
                                        japanese,
                                        word.get('hiragana', ''),
                                        word.get('kanji', ''),
                                        korean,
                                        word.get('level', 'N5'),
                                        word.get('category', '기타'),
                                        word.get('example_sentence', ''),
                                        word.get('example_korean', ''),
                                        word.get('memo_tip', '')
                                    ))
                                    added_count += 1
                            
                            conn.commit()
                            conn.close()
                            
                            st.success(f"✅ {added_count}개 단어가 추가되었습니다!")
                            st.balloons()
                    
                    except json.JSONDecodeError as e:
                        st.error(f"❌ JSON 형식 오류: {e}")
                else:
                    st.warning("JSON을 입력해주세요.")

# ===== 탭 2: 내 단어 목록 =====
with tab2:
    st.subheader("📋 내가 추가한 단어")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # is_user_added 컬럼 존재 확인 및 조회
    try:
        cursor.execute("SELECT * FROM words WHERE is_user_added = 1 ORDER BY id DESC")
        user_words = [dict(row) for row in cursor.fetchall()]
    except:
        # 컬럼이 없으면 빈 리스트
        user_words = []
    
    conn.close()
    
    if not user_words:
        st.info("아직 추가한 단어가 없습니다. '단어 추가' 탭에서 단어를 추가해보세요!")
    else:
        st.markdown(f"**총 {len(user_words)}개의 단어**")
        
        # 검색
        search = st.text_input("🔍 검색", placeholder="단어 검색...")
        
        if search:
            user_words = [w for w in user_words 
                        if search.lower() in w.get('japanese', '').lower()
                        or search.lower() in w.get('korean', '').lower()]
        
        for word in user_words:
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                with st.expander(f"**{word['japanese']}** - {word['korean']}"):
                    st.markdown(f"**히라가나:** {word.get('hiragana', '-')}")
                    st.markdown(f"**한자:** {word.get('kanji', '-')}")
                    st.markdown(f"**레벨:** {word.get('level', 'N5')} | **카테고리:** {word.get('category', '-')}")
                    
                    if word.get('example_sentence'):
                        st.markdown(f"**예문:** {word['example_sentence']}")
                        if word.get('example_korean'):
                            st.markdown(f"**번역:** {word['example_korean']}")
                    
                    if word.get('memo_tip'):
                        st.info(f"💡 {word['memo_tip']}")
            
            with col2:
                st.markdown(f"<small>{word.get('level', 'N5')}</small>", unsafe_allow_html=True)
            
            with col3:
                if st.button("🗑️", key=f"del_{word['id']}", help="삭제"):
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM words WHERE id = ?", (word['id'],))
                    conn.commit()
                    conn.close()
                    st.rerun()

# ===== 탭 3: 데이터 내보내기 =====
with tab3:
    st.subheader("📤 데이터 내보내기")
    
    st.markdown("추가한 단어를 JSON 파일로 내보내 백업할 수 있습니다.")
    
    export_option = st.radio(
        "내보낼 데이터",
        ["내가 추가한 단어만", "전체 단어"],
        horizontal=True
    )
    
    conn = get_connection()
    cursor = conn.cursor()
    
    if export_option == "내가 추가한 단어만":
        try:
            cursor.execute("SELECT * FROM words WHERE is_user_added = 1")
        except:
            cursor.execute("SELECT * FROM words WHERE 1=0")  # 빈 결과
    else:
        cursor.execute("SELECT * FROM words")
    
    words = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    if words:
        # JSON 변환
        export_data = []
        for w in words:
            export_data.append({
                "japanese": w.get('japanese', ''),
                "hiragana": w.get('hiragana', ''),
                "kanji": w.get('kanji', ''),
                "korean": w.get('korean', ''),
                "level": w.get('level', 'N5'),
                "category": w.get('category', ''),
                "example_sentence": w.get('example_sentence', ''),
                "example_korean": w.get('example_korean', ''),
                "memo_tip": w.get('memo_tip', '')
            })
        
        json_str = json.dumps(export_data, ensure_ascii=False, indent=2)
        
        st.download_button(
            label=f"📥 JSON 다운로드 ({len(words)}개 단어)",
            data=json_str,
            file_name="my_words.json",
            mime="application/json",
            use_container_width=True
        )
        
        with st.expander("📋 미리보기"):
            st.code(json_str[:2000] + ("..." if len(json_str) > 2000 else ""), language="json")
    else:
        st.info("내보낼 단어가 없습니다.")

# 사이드바
with st.sidebar:
    st.markdown("### 📊 단어 통계")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM words")
    total = cursor.fetchone()[0]
    
    try:
        cursor.execute("SELECT COUNT(*) FROM words WHERE is_user_added = 1")
        user_added = cursor.fetchone()[0]
    except:
        user_added = 0
    
    conn.close()
    
    st.markdown(f"**전체 단어:** {total}개")
    st.markdown(f"**기본 단어:** {total - user_added}개")
    st.markdown(f"**내가 추가:** {user_added}개")
    
    st.markdown("---")
    st.markdown("### 💡 팁")
    st.markdown("""
    - 추가한 단어는 퀴즈에 우선 출제됩니다
    - JSON으로 여러 단어를 한번에 추가하세요
    - 정기적으로 백업(내보내기)하세요
    """)
