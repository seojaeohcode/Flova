# 🎭 남도봇 축제 추천 시스템

AI 기반 멀티턴 대화형 남도 축제 추천 시스템입니다. 사용자의 선호도와 요구사항을 단계별로 파악하여 개인화된 축제를 추천하고, XAI(설명 가능한 AI) 방식으로 추천 이유를 설명합니다.

## ✨ 주요 기능

- **멀티턴 대화**: 사용자와 자연스러운 대화를 통해 선호도 파악
- **개인화 추천**: 여행 시기, 동반자, 분위기, 관심사 기반 맞춤 추천
- **XAI 설명**: 추천 이유와 TOP 랭킹 근거를 명확하게 제시
- **데이터베이스 연동**: MySQL을 통한 사용자 정보 및 추천 기록 관리
- **JWT 인증**: 안전한 사용자 인증 및 세션 관리
- **사용자 선호도 관리**: 개인화된 기본 설정 저장 및 활용

## 🏗️ 시스템 아키텍처

```
Frontend (다른 팀) ←→ Backend (FastAPI) ←→ MySQL Database
                           ↓
                    ClovaX LLM (향후 연동)
```

## 📁 프로젝트 구조

```
backend/actual/
├── namdo_bot.py          # 메인 FastAPI 애플리케이션
├── database.py           # 데이터베이스 모델 및 연결
├── auth.py              # 인증 시스템
├── models.py            # Pydantic 모델
├── crud.py              # 데이터베이스 CRUD 작업
├── requirements.txt     # Python 의존성
├── env_example.txt      # 환경 변수 예시
├── deploy.sh            # 배포 스크립트
└── README.md            # 프로젝트 문서
```

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
cp env_example.txt .env
# .env 파일을 편집하여 실제 데이터베이스 정보 입력
```

### 2. 데이터베이스 설정

```bash
# 데이터베이스 테이블 생성 및 초기 데이터 삽입
python database.py
```

### 3. 서버 실행

```bash
# 개발 서버 실행
python namdo_bot.py

# 또는 uvicorn 사용
uvicorn namdo_bot:app --host 0.0.0.0 --port 8000 --reload
```

### 4. API 문서 확인

브라우저에서 `http://localhost:8000/docs` 접속하여 Swagger UI 확인

## 🔐 API 명세서

### 📋 **인증 (Authentication)**

#### 1. 사용자 등록
- **엔드포인트**: `POST /register`
- **설명**: 새로운 사용자 계정 생성
- **요청 본문**:
```json
{
  "username": "string",
  "email": "user@example.com",
  "password": "string",
  "full_name": "string (optional)"
}
```
- **응답**: `UserInfo` 모델
- **상태 코드**: 200 (성공), 400 (잘못된 요청)

#### 2. 로그인
- **엔드포인트**: `POST /token`
- **설명**: 사용자 인증 및 JWT 토큰 발급
- **요청 본문**: `application/x-www-form-urlencoded`
  - `username`: 사용자명
  - `password`: 비밀번호
- **응답**: `Token` 모델
- **상태 코드**: 200 (성공), 401 (인증 실패)

#### 3. 사용자 정보 조회
- **엔드포인트**: `GET /users/me`
- **설명**: 현재 로그인된 사용자 정보 조회
- **인증**: Bearer Token 필요
- **응답**: `UserInfo` 모델
- **상태 코드**: 200 (성공), 401 (인증 필요)

### 👤 **사용자 선호도 관리 (User Preferences)**

#### 4. 사용자 선호도 조회
- **엔드포인트**: `GET /users/me/preferences`
- **설명**: 현재 사용자의 저장된 선호도 정보 조회
- **인증**: Bearer Token 필요
- **응답**: `List[UserPreference]`
- **상태 코드**: 200 (성공), 401 (인증 필요)

#### 5. 사용자 선호도 저장/업데이트
- **엔드포인트**: `POST /users/me/preferences`
- **설명**: 사용자 선호도 정보 저장 또는 업데이트
- **인증**: Bearer Token 필요
- **요청 본문**:
```json
{
  "preference_type": "string",
  "preference_value": "string"
}
```
- **응답**: `UserPreference` 모델
- **상태 코드**: 200 (성공), 401 (인증 필요)

### 🎭 **축제 추천 (Festival Recommendation)**

#### 6. 대화 초기화
- **엔드포인트**: `POST /initialize`
- **설명**: 축제 추천 대화 세션 시작
- **인증**: Bearer Token 필요
- **요청 본문**:
```json
{
  "travel_period": "string (예: 10월)",
  "companion_type": "string (예: 부모님 동반 가족)",
  "has_pets": "boolean (기본값: false)",
  "child_age_group": "string (optional)"
}
```
- **응답**: `ChatResponse` 모델
- **상태 코드**: 200 (성공), 401 (인증 필요)

#### 7. 대화 진행
- **엔드포인트**: `POST /chat`
- **설명**: 대화 세션에서 사용자 응답 처리
- **인증**: Bearer Token 필요
- **요청 본문**:
```json
{
  "session_id": "string",
  "user_response": "string",
  "selected_option": "string (optional)"
}
```
- **응답**: `ChatResponse` 모델
- **상태 코드**: 200 (성공), 401 (인증 필요), 404 (세션 없음)

#### 8. 추천 결과 조회
- **엔드포인트**: `GET /recommendations/{session_id}`
- **설명**: 완료된 대화 세션의 축제 추천 결과 조회
- **인증**: Bearer Token 필요
- **경로 매개변수**: `session_id` (대화 세션 ID)
- **응답**: `RecommendationResponse` 모델
- **상태 코드**: 200 (성공), 401 (인증 필요), 404 (세션 없음)

### 🏥 **시스템 상태 (Health)**

#### 9. 시스템 상태 확인
- **엔드포인트**: `GET /health`
- **설명**: 시스템 및 데이터베이스 연결 상태 확인
- **인증**: 불필요
- **응답**: `HealthCheck` 모델
- **상태 코드**: 200 (성공)

#### 10. 루트 엔드포인트
- **엔드포인트**: `GET /`
- **설명**: API 기본 정보 및 문서 링크
- **인증**: 불필요
- **응답**: 기본 메시지
- **상태 코드**: 200 (성공)

## 💬 대화 시나리오

### Phase 1: 초기 정보 입력
- 여행 시기 (월별)
- 동반자 유형 (혼자, 연인, 친구, 가족, 부모님 동반 등)
- 반려견 동반 여부
- 아이 연령대 (해당하는 경우)

### Phase 2: 대화형 선호도 파악
1. **분위기 선호도**: 활기찬 vs 여유로운
2. **핵심 관심사**: 자연, 음식, 역사/문화
3. **추가 요구사항**: 이동 편의성, 휴식 공간 등

### Phase 3: 최종 추천
- TOP 5 축제 추천
- 개인화된 추천 이유
- XAI 기반 설명

## 🗄️ 데이터베이스 스키마

### 주요 테이블

#### `users` - 사용자 정보
- `id`: 기본키
- `username`: 사용자명 (고유)
- `email`: 이메일 (고유)
- `hashed_password`: 암호화된 비밀번호
- `full_name`: 전체 이름
- `is_active`: 활성 상태
- `created_at`, `updated_at`: 생성/수정 시간

#### `conversations` - 대화 세션
- `id`: 기본키
- `session_id`: 세션 ID (고유)
- `user_id`: 사용자 ID (외래키)
- `travel_period`: 여행 시기
- `companion_type`: 동반자 유형
- `has_pets`: 반려견 동반 여부
- `child_age_group`: 아이 연령대
- `phase`: 대화 단계
- `energy_preference`: 에너지 레벨 선호도
- `interest_focus`: 관심사
- `additional_requirements`: 추가 요구사항
- `status`: 세션 상태
- `created_at`, `updated_at`: 생성/수정 시간

#### `conversation_messages` - 대화 메시지
- `id`: 기본키
- `conversation_id`: 대화 세션 ID (외래키)
- `role`: 메시지 역할 (user/assistant)
- `content`: 메시지 내용
- `turn_number`: 턴 번호
- `created_at`: 생성 시간

#### `user_preferences` - 사용자 선호도
- `id`: 기본키
- `user_id`: 사용자 ID (외래키)
- `preference_type`: 선호도 유형
- `preference_value`: 선호도 값

## 🔧 환경 변수

| 변수명 | 설명 | 기본값 |
|--------|------|--------|
| `DATABASE_URL` | MySQL 데이터베이스 연결 문자열 | - |
| `SECRET_KEY` | JWT 토큰 암호화 키 | - |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 토큰 만료 시간 | 30 |
| `HOST` | 서버 호스트 | 0.0.0.0 |
| `PORT` | 서버 포트 | 8000 |

## 📊 축제 추천 알고리즘

### 매칭 점수 계산
- **기본 점수**: 50점
- **계절 매칭**: +20점
- **에너지 레벨 매칭**: +15점
- **카테고리 매칭**: +20점
- **접근성 매칭**: +15점
- **추가 요구사항**: +10점

### 최대 점수: 100점

## 🧪 API 테스트 예시

### 1. 사용자 등록
```bash
curl -X POST "http://localhost:8000/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass",
    "full_name": "테스트 사용자"
  }'
```

### 2. 로그인
```bash
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=testpass"
```

### 3. 대화 초기화
```bash
curl -X POST "http://localhost:8000/initialize" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "travel_period": "10월",
    "companion_type": "부모님 동반 가족",
    "has_pets": false
  }'
```

### 4. 대화 진행
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "SESSION_ID",
    "user_response": "B. 너무 북적이는 건 싫고 좀 여유로운 게 좋겠어요.",
    "selected_option": "B"
  }'
```

### 5. 추천 결과 조회
```bash
curl -X GET "http://localhost:8000/recommendations/SESSION_ID" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🚀 네이버 클라우드 VPC 배포

### 1. 배포 스크립트 수정

```bash
# deploy.sh 파일에서 서버 정보 수정
SERVER_IP="your-actual-server-ip"
SERVER_USER="your-actual-username"
```

### 2. 배포 실행

```bash
# 배포 스크립트 실행 권한 부여
chmod +x deploy.sh

# 배포 실행
./deploy.sh
```

### 3. 서비스 관리

```bash
# 서비스 상태 확인
sudo systemctl status namdo-bot

# 서비스 재시작
sudo systemctl restart namdo-bot

# 로그 확인
sudo journalctl -u namdo-bot -f
```

## 🔮 향후 개발 계획

- [ ] ClovaX LLM 연동으로 더 자연스러운 대화 구현
- [ ] 실시간 추천 시스템 구축
- [ ] 사용자 피드백 기반 추천 정확도 향상
- [ ] 모바일 앱 API 지원
- [ ] 다국어 지원 (영어, 일본어 등)

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 문의

프로젝트 관련 문의사항이 있으시면 팀 리더에게 연락해주세요.

---

**남도봇 축제 추천 시스템** - 호남의 아름다운 축제를 AI와 함께 발견하세요! 🎭✨
