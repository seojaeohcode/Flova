# Flova 디렉토리 구조

```
Flova/
├── README.md
├── STRUCTURE.md
│
├── backend/
│   ├── actual/                      # 서비스 백엔드
│   │   ├── namdo_bot.py             # FastAPI 앱
│   │   ├── crud.py
│   │   ├── core/
│   │   │   ├── database.py
│   │   │   └── auth.py
│   │   ├── schemas/
│   │   │   └── models.py
│   │   ├── services/
│   │   │   ├── tour_api.py
│   │   │   └── festival_service.py
│   │   ├── scripts/
│   │   │   └── honam_festivals_to_csv.py
│   │   ├── requirements.txt
│   │   ├── deploy.sh
│   │   └── env_example.txt
│   │
│   └── example/
│       ├── LLM_RAG_example/
│       ├── check_db.py
│       └── test_mysql_connection.py
│
└── llm_relevant/                    # LLM·RAG
    ├── data/                        # CSV 데이터
    ├── rag/
    │   └── langchain_RAG.py
    ├── examples/
    ├── templates/
    ├── scripts/
    ├── requirements.txt
    ├── .gitignore
    └── LICENSE
```

자세한 설명은 `README.md` 참고.
