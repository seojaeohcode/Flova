# API 엔드포인트 상세 명세

실서버 실행 후 **Swagger UI** (`/docs`) 및 **ReDoc** (`/redoc`)에서 대화형 문서를 확인할 수 있습니다.

---

## 인증 관련 API

| Method | URL | 설명 | 인증 |
|--------|-----|------|------|
| POST | `/auth/register` | 회원가입 | 불필요 |
| POST | `/auth/login` | 로그인 | 불필요 |
| GET | `/users/me` | 사용자 정보 조회 | Bearer |
| PUT | `/users/me/profile` | 프로필 업데이트 | Bearer |

### POST /auth/register (회원가입)
- **Request**: `username`, `email`, `full_name`, `password` (JSON)
- **Response (201)**: 사용자 정보 (id, username, email, full_name, profile_picture, is_active, created_at)
- **Error (400)**: "이미 존재하는 사용자명입니다." 등

### POST /auth/login (로그인)
- **Request**: `username`, `password` (JSON)
- **Response (200)**: `access_token`, `token_type`, `user` 객체
- **Error (401)**: "잘못된 사용자명 또는 비밀번호입니다."

### GET /users/me
- **Headers**: `Authorization: Bearer {token}`
- **Response (200)**: 사용자 상세 정보

### PUT /users/me/profile
- **Request**: `full_name`, `profile_picture` (선택)
- **Response (200)**: 업데이트된 사용자 정보

---

## 봇 관련 API

| Method | URL | 설명 | 인증 |
|--------|-----|------|------|
| POST | `/bot/greeting` | 봇 인사말 및 첫 질문 | Bearer |
| POST | `/bot/finalize` | XAI 최종 추천 | Bearer |

### POST /bot/greeting
- **Request**: `travel_period`, `companion_type` (예: "10월", "부모님 동반 가족")
- **Response (200)**: `greeting_message`, `next_question`, `choices`, `session_id`, `phase`, `status`

### POST /bot/finalize
- **Request**: `session_id` (UUID)
- **Response (200)**: `user_profile`, `recommendation_summary`, `top_recommendation`, `alternative_recommendations`, `score_breakdown`, `recommendation_criteria`, `reasoning_summary`, `timestamp`

---

## 축제 관련 API

| Method | URL | 설명 | 인증 |
|--------|-----|------|------|
| POST | `/festivals/collect` | 축제 데이터 수집 (관리자) | Bearer |
| GET | `/festivals/search` | 축제 검색·필터링 | Bearer |
| POST | `/festivals/recommend` | 축제 직접 추천 | Bearer |

### GET /festivals/search
- **Query**: `region`, `period`, `festival_type`, `has_pet_info`, `page`, `limit`
- **Response (200)**: `festivals` 배열, `pagination` (page, limit, total, pages)

### POST /festivals/recommend
- **Request**: `travel_period`, `companion_type`, `atmosphere`, `core_experience`, `additional_considerations`
- **Response (200)**: `recommendations` (festival, score, reasons), `total_count`

---

## 시스템 관련 API

| Method | URL | 설명 | 인증 |
|--------|-----|------|------|
| GET | `/` | 루트 환영 메시지 | 불필요 |
| GET | `/health` | 헬스 체크 | 불필요 |

### GET /health
- **Response (200)**: `message`, `status`, `timestamp`, `version`, `database`, `llm_service`

---

[← 데이터베이스](03-database.md) | [메인 README](../README.md) | [다음: 배포 방법 →](05-deployment.md)
