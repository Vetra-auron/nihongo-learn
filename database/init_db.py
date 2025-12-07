import sqlite3
import json
import os
from datetime import datetime, date

DB_PATH = os.path.join(os.path.dirname(__file__), 'nihongo.db')

def get_connection():
    """데이터베이스 연결 반환"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """데이터베이스 테이블 초기화"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 단어 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            japanese TEXT NOT NULL,
            hiragana TEXT,
            kanji TEXT,
            korean TEXT NOT NULL,
            level TEXT DEFAULT 'N5',
            category TEXT,
            example_sentence TEXT,
            example_korean TEXT,
            memo_tip TEXT,
            is_user_added INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # is_user_added 컬럼이 없으면 추가 (기존 DB 호환)
    try:
        cursor.execute("ALTER TABLE words ADD COLUMN is_user_added INTEGER DEFAULT 0")
    except:
        pass  # 이미 존재하면 무시
    
    # 문법 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS grammars (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pattern TEXT NOT NULL,
            meaning TEXT NOT NULL,
            explanation TEXT,
            level TEXT DEFAULT 'N5',
            connection_rule TEXT,
            example_sentence TEXT,
            example_korean TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 학습 기록 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS learning_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content_type TEXT NOT NULL,
            content_id INTEGER NOT NULL,
            learned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            review_count INTEGER DEFAULT 0,
            next_review DATE,
            mastery_level INTEGER DEFAULT 0
        )
    ''')
    
    # 퀴즈 결과 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quiz_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quiz_type TEXT NOT NULL,
            score INTEGER NOT NULL,
            total_questions INTEGER NOT NULL,
            details TEXT,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 오답 기록 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS wrong_answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_type TEXT NOT NULL,
            content_type TEXT NOT NULL,
            content_id INTEGER NOT NULL,
            wrong_count INTEGER DEFAULT 1,
            last_wrong_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            resolved INTEGER DEFAULT 0
        )
    ''')
    
    # 출석 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE UNIQUE NOT NULL,
            study_minutes INTEGER DEFAULT 0,
            words_learned INTEGER DEFAULT 0,
            quiz_taken INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 일일 학습 할당 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_assignment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE NOT NULL,
            content_type TEXT NOT NULL,
            content_id INTEGER NOT NULL,
            completed INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ 데이터베이스 초기화 완료!")

def load_initial_data():
    """초기 데이터 로드"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 이미 데이터가 있는지 확인
    cursor.execute("SELECT COUNT(*) FROM words")
    if cursor.fetchone()[0] > 0:
        print("ℹ️ 이미 데이터가 존재합니다.")
        conn.close()
        return
    
    # 단어 데이터 로드
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    words_file = os.path.join(data_dir, 'words_n5.json')
    grammar_file = os.path.join(data_dir, 'grammar_n5.json')
    
    if os.path.exists(words_file):
        with open(words_file, 'r', encoding='utf-8') as f:
            words = json.load(f)
            for word in words:
                cursor.execute('''
                    INSERT INTO words (japanese, hiragana, kanji, korean, level, category, example_sentence, example_korean, memo_tip)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    word.get('japanese', ''),
                    word.get('hiragana', ''),
                    word.get('kanji', ''),
                    word.get('korean', ''),
                    word.get('level', 'N5'),
                    word.get('category', ''),
                    word.get('example_sentence', ''),
                    word.get('example_korean', ''),
                    word.get('memo_tip', '')
                ))
        print(f"✅ {len(words)}개의 단어 데이터 로드 완료!")
    
    if os.path.exists(grammar_file):
        with open(grammar_file, 'r', encoding='utf-8') as f:
            grammars = json.load(f)
            for grammar in grammars:
                cursor.execute('''
                    INSERT INTO grammars (pattern, meaning, explanation, level, connection_rule, example_sentence, example_korean)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    grammar.get('pattern', ''),
                    grammar.get('meaning', ''),
                    grammar.get('explanation', ''),
                    grammar.get('level', 'N5'),
                    grammar.get('connection_rule', ''),
                    grammar.get('example_sentence', ''),
                    grammar.get('example_korean', '')
                ))
        print(f"✅ {len(grammars)}개의 문법 데이터 로드 완료!")
    
    conn.commit()
    conn.close()

def check_attendance_today():
    """오늘 출석 체크"""
    conn = get_connection()
    cursor = conn.cursor()
    today = date.today().isoformat()
    
    cursor.execute("SELECT * FROM attendance WHERE date = ?", (today,))
    result = cursor.fetchone()
    
    if not result:
        cursor.execute("INSERT INTO attendance (date) VALUES (?)", (today,))
        conn.commit()
        print("✅ 오늘 출석 체크!")
    
    conn.close()
    return True

def update_attendance(words_learned=0, quiz_taken=0, study_minutes=0):
    """출석 정보 업데이트"""
    conn = get_connection()
    cursor = conn.cursor()
    today = date.today().isoformat()
    
    cursor.execute('''
        UPDATE attendance 
        SET words_learned = words_learned + ?,
            quiz_taken = quiz_taken + ?,
            study_minutes = study_minutes + ?
        WHERE date = ?
    ''', (words_learned, quiz_taken, study_minutes, today))
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_database()
    load_initial_data()
