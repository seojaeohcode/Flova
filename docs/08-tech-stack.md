# 기술 스택

| 영역 | 기술 | 비고 |
|------|------|------|
| Backend | FastAPI 0.116+ | ASGI, Swagger/ReDoc, OpenAPI |
| DB·ORM | SQLAlchemy 2.x, MySQL 8.x | 연결 풀, utf8mb4 |
| AI/LLM | LangChain 0.3.x, Clova Studio | RAG, 프롬프트·메모리 |
| 인증 | PyJWT, bcrypt | JWT, 비밀번호 해싱 |
| 검증·데이터 | Pydantic 2.x, FAISS | 스키마 검증, 벡터 검색 |
| 외부 API | TourAPI, Requests | 관광공사 API, HTTP |
| 배포 | 네이버 클라우드 VPC, systemd | 서비스 관리, 로그 |
| 개발 | Python 3.8+, uvicorn, python-dotenv | ASGI 서버, 환경 변수 |

- **문서**: `/docs` (Swagger UI), `/redoc` (ReDoc), OpenAPI 3.0

[← 주요 기능](07-features.md) | [메인 README](../README.md) | [다음: API 사용 예시 →](09-api-examples.md)
