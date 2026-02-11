# 프로젝트 구조

전체 디렉터리 트리는 루트의 [STRUCTURE.md](../STRUCTURE.md)에도 동일하게 정리되어 있습니다.

---

## 디렉터리 트리

```
Flova/
├── README.md
├── STRUCTURE.md
├── docs/                           # 문서 (내용별 분리)
│   ├── 01-overview.md
│   ├── 02-structure.md
│   ├── 03-database.md
│   ├── 04-api.md
│   ├── 05-deployment.md
│   ├── 06-environment.md
│   ├── 07-features.md
│   ├── 08-tech-stack.md
│   ├── 09-api-examples.md
│   ├── 10-operations.md
│   └── 11-license.md
│
├── backend/
│   ├── actual/                     # 서비스 백엔드 (운영)
│   │   ├── namdo_bot.py            # FastAPI 앱 진입점
│   │   ├── crud.py                 # DB CRUD
│   │   ├── core/
│   │   │   ├── database.py         # SQLAlchemy 모델·세션
│   │   │   └── auth.py             # JWT 인증
│   │   ├── schemas/
│   │   │   └── models.py           # Pydantic 요청/응답 모델
│   │   ├── services/
│   │   │   ├── tour_api.py         # 관광공사 API 클라이언트
│   │   │   └── festival_service.py # 축제 수집·추천 서비스
│   │   ├── scripts/
│   │   │   └── honam_festivals_to_csv.py  # 축제 → CSV 수집
│   │   ├── requirements.txt
│   │   ├── deploy.sh
│   │   └── env_example.txt
│   └── example/                    # 예제·테스트
│       ├── LLM_RAG_example/
│       ├── check_db.py
│       └── test_mysql_connection.py
│
└── llm_relevant/                   # LLM·RAG 실험·예제
    ├── data/                       # CSV 데이터
    │   ├── honam_festivals_base.csv
    │   ├── honam_festivals_common.csv
    │   └── honam_festivals_intro.csv
    ├── rag/
    │   └── langchain_RAG.py        # LangChain RAG (CSV → FAISS)
    ├── examples/
    │   ├── 01_llm.py ~ 05_chatbot.py, 원래_03.py
    ├── templates/
    │   └── index.html
    ├── scripts/
    │   ├── honam_festivals_to_csv.py
    │   └── tour_api.py
    ├── requirements.txt
    ├── .gitignore
    └── LICENSE
```

---

## 실행 방법

| 목적 | 위치 | 명령 |
|------|------|------|
| 백엔드 서버 | `backend/actual` | `python namdo_bot.py` 또는 `uvicorn namdo_bot:app --reload` |
| 축제 CSV 수집 (백엔드) | `backend/actual` | `python scripts/honam_festivals_to_csv.py` |
| RAG 실행 | `llm_relevant` | `python rag/langchain_RAG.py` (데이터는 `data/` 사용) |

[← 개요](01-overview.md) | [메인 README](../README.md) | [다음: 데이터베이스 스키마 →](03-database.md)
