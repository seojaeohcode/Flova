# 남도봇 축제 추천 시스템 (Namdo Bot)

AI 기반 멀티턴 대화형 **남도 축제 추천** 시스템입니다. LangChain·ClovaX LLM으로 사용자 맞춤 추천, TourAPI로 실시간 축제 정보를 제공합니다.

---

## 문서 목차 (내용별 분리)

문서는 `docs/` 폴더에 주제별로 나뉘어 있습니다.

| 문서 | 내용 |
|------|------|
| [docs/01-overview.md](docs/01-overview.md) | 프로젝트 개요, 핵심 목표, 서비스 지역, 주요 특징, 시스템 아키텍처 |
| [docs/02-structure.md](docs/02-structure.md) | 프로젝트 구조(디렉터리 트리), 실행 방법 |
| [docs/03-database.md](docs/03-database.md) | 데이터베이스 스키마, 테이블·관계도, 인덱스, 제약조건 |
| [docs/04-api.md](docs/04-api.md) | API 엔드포인트 명세 (인증, 봇, 축제, 시스템) |
| [docs/05-deployment.md](docs/05-deployment.md) | 배포 방법 (VPC, systemd, 로그·모니터링) |
| [docs/06-environment.md](docs/06-environment.md) | 환경 변수(.env), API 키 발급, 보안 |
| [docs/07-features.md](docs/07-features.md) | 주요 기능 (AI 추천, 대화, XAI, TourAPI, 보안) |
| [docs/08-tech-stack.md](docs/08-tech-stack.md) | 기술 스택 요약 |
| [docs/09-api-examples.md](docs/09-api-examples.md) | API 사용 예시 (curl, Python 클라이언트) |
| [docs/10-operations.md](docs/10-operations.md) | 문제 해결, 성능 최적화, 향후 계획 |
| [docs/11-license.md](docs/11-license.md) | 라이선스, 기여 방법, 문의 |

디렉터리 트리만 빠르게 보려면 [STRUCTURE.md](STRUCTURE.md) 를 참고하세요.

---

## 빠른 시작

```bash
# 백엔드 서버 (backend/actual 에서)
cd backend/actual
python namdo_bot.py
# 또는: uvicorn namdo_bot:app --reload

# 축제 CSV 수집 (백엔드)
cd backend/actual
python scripts/honam_festivals_to_csv.py

# RAG 실행 (llm_relevant)
cd llm_relevant
python rag/langchain_RAG.py
```

`.env` 설정은 [docs/06-environment.md](docs/06-environment.md) 와 `backend/actual/env_example.txt` 를 참고하세요.

---

## 프로젝트 구조 요약

```
Flova/
├── README.md          ← 현재 문서
├── STRUCTURE.md       ← 디렉터리 트리
├── docs/              ← 위 목차의 분리 문서
├── backend/actual/    ← 서비스 백엔드 (core, schemas, services, scripts)
└── llm_relevant/      ← LLM·RAG (data, rag, examples, templates, scripts)
```

자세한 트리와 실행 방법은 [docs/02-structure.md](docs/02-structure.md) 또는 [STRUCTURE.md](STRUCTURE.md) 에 있습니다.
