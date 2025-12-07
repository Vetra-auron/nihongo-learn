# 🇯🇵 일본어 학습 웹앱 (にほんご)

매일 조금씩 일본어를 학습할 수 있는 웹 애플리케이션입니다.

## ✨ 주요 기능

### 📚 단어장
- JLPT N5 레벨 80개 이상의 단어 수록
- 예문과 암기 팁 제공
- 카테고리별, 레벨별 필터링
- 검색 기능

### 📖 문법
- N5 필수 문법 30개 수록
- 접속 규칙 및 예문 제공
- 상세 설명

### 🎯 퀴즈
- **1단계**: 오늘의 학습 범위 (10문제)
- **2단계**: 전체 복습 (20문제)
- 단어 + 문법 혼합 출제
- 힌트 기능

### 📝 오답노트
- 틀린 문제 자동 기록
- 틀린 횟수별 우선순위
- 취약 분야 분석

### 📊 성과
- 연속 출석일 (스트릭)
- 퀴즈 점수 추이
- 학습 진도 현황
- 목표 달성 배지

---

## 🚀 설치 및 실행

### 1. 요구사항
- Python 3.8 이상
- pip

### 2. 설치

```bash
# 프로젝트 폴더로 이동
cd nihongo-learn

# 가상환경 생성 (권장)
python -m venv venv

# 가상환경 활성화
# Mac/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt
```

### 3. 실행

```bash
streamlit run app.py
```

브라우저에서 `http://localhost:8501` 로 접속하세요!

---

## 📁 프로젝트 구조

```
nihongo-learn/
├── app.py                    # 메인 앱 (대시보드)
├── requirements.txt          # 패키지 목록
├── README.md
├── database/
│   ├── __init__.py
│   ├── init_db.py           # DB 초기화 및 모델
│   └── nihongo.db           # SQLite DB (자동 생성)
├── pages/
│   ├── 1_📚_단어장.py
│   ├── 2_📖_문법.py
│   ├── 3_🎯_퀴즈.py
│   ├── 4_📝_오답노트.py
│   └── 5_📊_성과.py
├── data/
│   ├── words_n5.json        # N5 단어 데이터
│   └── grammar_n5.json      # N5 문법 데이터
└── utils/
    ├── __init__.py
    └── quiz_generator.py    # 퀴즈 생성 로직
```

---

## 🔧 커스터마이징

### 단어 추가하기

`data/words_n5.json` 파일에 다음 형식으로 추가:

```json
{
    "japanese": "새 단어",
    "hiragana": "読み方",
    "kanji": "漢字",
    "korean": "한국어 뜻",
    "level": "N5",
    "category": "카테고리",
    "example_sentence": "예문",
    "example_korean": "예문 번역",
    "memo_tip": "암기 팁"
}
```

### 문법 추가하기

`data/grammar_n5.json` 파일에 추가

---

## 🌐 배포

### Streamlit Cloud (무료)

1. GitHub에 프로젝트 업로드
2. [share.streamlit.io](https://share.streamlit.io) 접속
3. GitHub 연동 후 배포

---

## 📝 업데이트 예정

- [ ] AI 예문 생성 (Claude API 연동)
- [ ] N4~N1 레벨 확장
- [ ] 음성 재생 기능
- [ ] 소셜 로그인
- [ ] 학습 리마인더

---

## 📄 라이선스

MIT License

---

**즐거운 일본어 학습 되세요! 🎌**
