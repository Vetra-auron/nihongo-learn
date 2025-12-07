import random
import sqlite3
import os
from datetime import date

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'nihongo.db')

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_today_words(limit=5):
    """오늘의 학습 단어 가져오기 (사용자 추가 단어 우선)"""
    conn = get_connection()
    cursor = conn.cursor()
    today = date.today().isoformat()
    
    # 오늘 할당된 단어 확인
    cursor.execute("""
        SELECT w.* FROM words w
        JOIN daily_assignment da ON w.id = da.content_id
        WHERE da.date = ? AND da.content_type = 'word'
    """, (today,))
    
    assigned_words = [dict(row) for row in cursor.fetchall()]
    
    # 할당된 단어가 없으면 새로 할당
    if not assigned_words:
        # 1순위: 사용자가 추가한 단어 중 아직 학습하지 않은 것
        cursor.execute("""
            SELECT w.* FROM words w
            LEFT JOIN learning_history lh ON w.id = lh.content_id AND lh.content_type = 'word'
            WHERE lh.id IS NULL AND w.is_user_added = 1
            ORDER BY RANDOM()
            LIMIT ?
        """, (limit,))
        new_words = list(cursor.fetchall())
        
        # 2순위: 부족하면 일반 단어 중 학습하지 않은 것 추가
        if len(new_words) < limit:
            remaining = limit - len(new_words)
            cursor.execute("""
                SELECT w.* FROM words w
                LEFT JOIN learning_history lh ON w.id = lh.content_id AND lh.content_type = 'word'
                WHERE lh.id IS NULL AND (w.is_user_added = 0 OR w.is_user_added IS NULL)
                ORDER BY RANDOM()
                LIMIT ?
            """, (remaining,))
            new_words.extend(cursor.fetchall())
        
        # 3순위: 그래도 부족하면 전체에서 랜덤
        if len(new_words) < limit:
            cursor.execute("""
                SELECT w.* FROM words w
                ORDER BY w.is_user_added DESC, RANDOM()
                LIMIT ?
            """, (limit,))
            new_words = list(cursor.fetchall())
        
        # 오늘 할당에 추가
        for word in new_words:
            cursor.execute("""
                INSERT INTO daily_assignment (date, content_type, content_id)
                VALUES (?, 'word', ?)
            """, (today, word['id']))
        
        conn.commit()
        assigned_words = [dict(row) for row in new_words]
    
    conn.close()
    return assigned_words

def get_learned_words():
    """지금까지 학습한 모든 단어"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT DISTINCT w.* FROM words w
        JOIN learning_history lh ON w.id = lh.content_id
        WHERE lh.content_type = 'word'
    """)
    
    words = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    # 학습 기록이 없으면 모든 단어 반환
    if not words:
        return get_all_words()
    
    return words

def get_all_words():
    """모든 단어 (사용자 추가 단어 우선)"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM words ORDER BY is_user_added DESC, id DESC")
    words = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return words

def get_user_added_words():
    """사용자가 추가한 단어만"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM words WHERE is_user_added = 1 ORDER BY id DESC")
        words = [dict(row) for row in cursor.fetchall()]
    except:
        words = []
    conn.close()
    return words

def get_all_grammars():
    """모든 문법"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM grammars")
    grammars = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return grammars

def mark_word_learned(word_id):
    """단어 학습 완료 표시"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 기존 기록 확인
    cursor.execute("""
        SELECT id FROM learning_history
        WHERE content_type = 'word' AND content_id = ?
    """, (word_id,))
    
    existing = cursor.fetchone()
    
    if existing:
        cursor.execute("""
            UPDATE learning_history
            SET review_count = review_count + 1, learned_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (existing['id'],))
    else:
        cursor.execute("""
            INSERT INTO learning_history (content_type, content_id)
            VALUES ('word', ?)
        """, (word_id,))
    
    conn.commit()
    conn.close()

def generate_word_quiz(words, num_questions=10):
    """단어 퀴즈 생성"""
    if len(words) < 4:
        return []
    
    questions = []
    quiz_words = random.sample(words, min(num_questions, len(words)))
    
    for word in quiz_words:
        # 오답 보기 생성
        other_words = [w for w in words if w['id'] != word['id']]
        wrong_answers = random.sample(other_words, min(3, len(other_words)))
        
        # 문제 유형 결정 (일본어 → 한국어 / 한국어 → 일본어)
        question_type = random.choice(['jp_to_kr', 'kr_to_jp'])
        
        if question_type == 'jp_to_kr':
            question = {
                'type': 'word',
                'question_type': 'jp_to_kr',
                'question': f"「{word['japanese']}」의 뜻은?",
                'correct_answer': word['korean'],
                'options': [word['korean']] + [w['korean'] for w in wrong_answers],
                'word_id': word['id'],
                'hint': word.get('memo_tip', '')
            }
        else:
            question = {
                'type': 'word',
                'question_type': 'kr_to_jp',
                'question': f"「{word['korean']}」을(를) 일본어로?",
                'correct_answer': word['japanese'],
                'options': [word['japanese']] + [w['japanese'] for w in wrong_answers],
                'word_id': word['id'],
                'hint': word.get('memo_tip', '')
            }
        
        random.shuffle(question['options'])
        questions.append(question)
    
    return questions

def generate_grammar_quiz(grammars, num_questions=5):
    """문법 퀴즈 생성"""
    if len(grammars) < 4:
        return []
    
    questions = []
    quiz_grammars = random.sample(grammars, min(num_questions, len(grammars)))
    
    for grammar in quiz_grammars:
        other_grammars = [g for g in grammars if g['id'] != grammar['id']]
        wrong_answers = random.sample(other_grammars, min(3, len(other_grammars)))
        
        question = {
            'type': 'grammar',
            'question': f"「{grammar['pattern']}」의 의미는?",
            'correct_answer': grammar['meaning'],
            'options': [grammar['meaning']] + [g['meaning'] for g in wrong_answers],
            'grammar_id': grammar['id'],
            'hint': grammar.get('explanation', '')
        }
        
        random.shuffle(question['options'])
        questions.append(question)
    
    return questions

def generate_full_quiz(quiz_type='today', word_count=7, grammar_count=3):
    """전체 퀴즈 생성 (단어 + 문법) - 사용자 추가 단어 우선"""
    if quiz_type == 'today':
        words = get_today_words(10)
    else:
        # 사용자 추가 단어 우선으로 가져오기
        user_words = get_user_added_words()
        learned_words = get_learned_words()
        
        # 사용자 추가 단어를 앞에 배치
        words = user_words.copy()
        for w in learned_words:
            if w['id'] not in [uw['id'] for uw in user_words]:
                words.append(w)
    
    grammars = get_all_grammars()
    
    word_questions = generate_word_quiz(words, word_count)
    grammar_questions = generate_grammar_quiz(grammars, grammar_count)
    
    all_questions = word_questions + grammar_questions
    random.shuffle(all_questions)
    
    return all_questions

def save_quiz_result(quiz_type, score, total, details=None):
    """퀴즈 결과 저장"""
    import json
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO quiz_results (quiz_type, score, total_questions, details)
        VALUES (?, ?, ?, ?)
    """, (quiz_type, score, total, json.dumps(details) if details else None))
    
    conn.commit()
    conn.close()

def save_wrong_answer(question_type, content_type, content_id):
    """오답 기록 저장"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 기존 오답 기록 확인
    cursor.execute("""
        SELECT id, wrong_count FROM wrong_answers
        WHERE question_type = ? AND content_type = ? AND content_id = ?
    """, (question_type, content_type, content_id))
    
    existing = cursor.fetchone()
    
    if existing:
        cursor.execute("""
            UPDATE wrong_answers
            SET wrong_count = wrong_count + 1, last_wrong_at = CURRENT_TIMESTAMP, resolved = 0
            WHERE id = ?
        """, (existing['id'],))
    else:
        cursor.execute("""
            INSERT INTO wrong_answers (question_type, content_type, content_id)
            VALUES (?, ?, ?)
        """, (question_type, content_type, content_id))
    
    conn.commit()
    conn.close()

def get_wrong_answers():
    """오답 노트 조회"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 단어 오답
    cursor.execute("""
        SELECT wa.*, w.japanese, w.korean, w.hiragana, w.memo_tip
        FROM wrong_answers wa
        JOIN words w ON wa.content_id = w.id
        WHERE wa.content_type = 'word' AND wa.resolved = 0
        ORDER BY wa.wrong_count DESC, wa.last_wrong_at DESC
    """)
    word_wrongs = [dict(row) for row in cursor.fetchall()]
    
    # 문법 오답
    cursor.execute("""
        SELECT wa.*, g.pattern, g.meaning, g.explanation
        FROM wrong_answers wa
        JOIN grammars g ON wa.content_id = g.id
        WHERE wa.content_type = 'grammar' AND wa.resolved = 0
        ORDER BY wa.wrong_count DESC, wa.last_wrong_at DESC
    """)
    grammar_wrongs = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return {'words': word_wrongs, 'grammars': grammar_wrongs}

def resolve_wrong_answer(wrong_id):
    """오답 해결 표시"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE wrong_answers SET resolved = 1 WHERE id = ?", (wrong_id,))
    conn.commit()
    conn.close()

def get_statistics():
    """학습 통계 조회"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 총 학습 단어 수
    cursor.execute("SELECT COUNT(DISTINCT content_id) FROM learning_history WHERE content_type = 'word'")
    learned_words = cursor.fetchone()[0]
    
    # 총 단어 수
    cursor.execute("SELECT COUNT(*) FROM words")
    total_words = cursor.fetchone()[0]
    
    # 사용자 추가 단어 수
    try:
        cursor.execute("SELECT COUNT(*) FROM words WHERE is_user_added = 1")
        user_added_words = cursor.fetchone()[0]
    except:
        user_added_words = 0
    
    # 퀴즈 통계
    cursor.execute("""
        SELECT 
            COUNT(*) as total_quizzes,
            AVG(score * 100.0 / total_questions) as avg_score,
            MAX(score * 100.0 / total_questions) as best_score
        FROM quiz_results
    """)
    quiz_stats = dict(cursor.fetchone())
    
    # 출석 통계
    cursor.execute("""
        SELECT COUNT(*) as total_days,
               SUM(words_learned) as total_words_learned,
               SUM(quiz_taken) as total_quizzes_taken
        FROM attendance
    """)
    attendance_stats = dict(cursor.fetchone())
    
    # 연속 출석일 계산
    cursor.execute("""
        SELECT date FROM attendance ORDER BY date DESC
    """)
    dates = [row['date'] for row in cursor.fetchall()]
    
    streak = 0
    if dates:
        from datetime import datetime, timedelta
        today = date.today()
        for i, d in enumerate(dates):
            expected_date = (today - timedelta(days=i)).isoformat()
            if d == expected_date:
                streak += 1
            else:
                break
    
    conn.close()
    
    return {
        'learned_words': learned_words,
        'total_words': total_words,
        'user_added_words': user_added_words,
        'quiz_count': quiz_stats['total_quizzes'] or 0,
        'avg_score': round(quiz_stats['avg_score'] or 0, 1),
        'best_score': round(quiz_stats['best_score'] or 0, 1),
        'total_study_days': attendance_stats['total_days'] or 0,
        'streak': streak
    }

def get_recent_quiz_results(limit=10):
    """최근 퀴즈 결과"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM quiz_results
        ORDER BY completed_at DESC
        LIMIT ?
    """, (limit,))
    
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results

def get_attendance_history(days=30):
    """출석 기록"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM attendance
        ORDER BY date DESC
        LIMIT ?
    """, (days,))
    
    records = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return records
