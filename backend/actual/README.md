# 🎯 남도봇 축제 추천 시스템 (Namdo Bot Festival Recommendation System)

AI 기반 멀티턴 대화형 남도 축제 추천 시스템으로, LangChain과 ClovaX LLM을 활용하여 사용자 맞춤형 축제를 추천합니다.

## 🌟 주요 특징

- **🤖 AI 기반 추천**: LangChain + ClovaX LLM으로 지능적인 축제 추천
- **🔒 구조화된 JSON 응답**: PydanticOutputParser로 안정적인 API 응답
- **🗄️ 완벽한 데이터베이스**: MySQL 기반 사용자 관리 및 대화 세션 추적
- **🌐 외부 API 연동**: TourAPI(공공데이터포털)를 통한 실시간 축제 정보
- **🚀 자동화된 배포**: VPC 서버 자동 배포 및 서비스 관리

## 🏗️ 시스템 아키텍처

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   FastAPI       │    │   MySQL DB      │
│   (React/Vue)   │◄──►│   Backend       │◄──►│   (네이버 클라우드)│
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   LangChain     │
                       │   + ClovaX      │
                       │   LLM           │
                       └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   TourAPI       │
                       │   (공공데이터포털) │
                       └─────────────────┘
```

## 📁 프로젝트 구조

```
backend/actual/
├── namdo_bot.py          # 🚀 메인 FastAPI 애플리케이션
├── database.py            # 🗄️ SQLAlchemy 데이터베이스 모델
├── models.py              # 📋 Pydantic API 모델
├── crud.py                # 🔧 데이터베이스 CRUD 작업
├── auth.py                # 🔐 JWT 인증 및 사용자 관리
├── festival_service.py    # 🌐 TourAPI 연동 및 축제 서비스
├── tour_api.py            # 📡 공공데이터포털 API 클라이언트
├── honam_festivals_to_csv.py  # 📊 축제 데이터 수집 스크립트
├── requirements.txt       # 📦 Python 의존성
├── deploy.sh              # 🚀 VPC 배포 스크립트
├── env_example.txt        # ⚙️ 환경 변수 예시
└── README.md              # 📖 프로젝트 문서
```

## 🗄️ 데이터베이스 스키마

### Users 테이블
```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    profile_picture VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### Conversations 테이블
```sql
CREATE TABLE conversations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    travel_period VARCHAR(50),
    companion_type VARCHAR(100),
    has_pets BOOLEAN DEFAULT FALSE,
    child_age_group VARCHAR(50),
    energy_preference VARCHAR(100),
    interest_focus VARCHAR(100),
    additional_requirements TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### Festivals 테이블
```sql
CREATE TABLE festivals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    contentid VARCHAR(50) UNIQUE NOT NULL,
    title VARCHAR(500) NOT NULL,
    contenttypeid VARCHAR(50),
    addr1 VARCHAR(500),
    start_date VARCHAR(20),
    end_date VARCHAR(20),
    image VARCHAR(1000),
    progresstype VARCHAR(100),
    festivaltype VARCHAR(100),
    tel VARCHAR(100),
    region VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🔌 API 엔드포인트

### 🔐 인증 관련
- **POST** `/auth/register` - 회원가입
- **POST** `/auth/login` - 로그인
- **GET** `/users/me` - 사용자 정보 조회
- **PUT** `/users/me/profile` - 프로필 업데이트

### 🤖 봇 관련
- **POST** `/bot/greeting` - 봇 인사말 및 첫 질문
- **POST** `/bot/finalize` - XAI 기반 최종 추천

### 🎉 축제 관련
- **POST** `/festivals/collect` - 축제 데이터 수집 (관리자)
- **GET** `/festivals/search` - 축제 검색
- **POST** `/festivals/recommend` - 축제 추천

### 🏥 시스템 관련
- **GET** `/` - 루트 엔드포인트
- **GET** `/health` - 헬스 체크

## 🚀 배포 방법

### 1. 사전 준비
- 네이버 클라우드 VPC 서버 준비
- MySQL 데이터베이스 설정
- SSH 접근 권한

### 2. 배포 실행
```bash
cd backend/actual
bash deploy.sh
```

### 3. 배포 후 확인
```bash
# 서비스 상태 확인
sudo systemctl status namdo-bot

# 로그 확인
sudo journalctl -u namdo-bot -f

# API 테스트
curl http://localhost:8000/health
```

## ⚙️ 환경 변수 설정

`.env` 파일에 다음 변수들을 설정해야 합니다:

```bash
# 데이터베이스 설정
DATABASE_URL=mysql+pymysql://username:password@host:port/database?charset=utf8mb4

# API 키
TOUR_API_KEY=your_tour_api_key_here
CLOVASTUDIO_API_KEY=your_clovastudio_api_key_here

# JWT 설정
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## 🔧 주요 기능

### 1. AI 기반 축제 추천
- **LangChain RAG 시스템**: 사용자 선호도 기반 지능형 추천
- **ClovaX LLM**: 네이버의 최신 AI 모델 활용
- **구조화된 JSON 응답**: PydanticOutputParser로 안정적인 출력

### 2. 멀티턴 대화 시스템
- **사용자 프로필 수집**: 여행 시기, 동반자, 선호도 등
- **점진적 정보 수집**: 단계별 질문을 통한 정확한 추천
- **대화 세션 관리**: 사용자별 대화 히스토리 추적

### 3. XAI (Explainable AI)
- **추천 이유 설명**: 왜 이 축제를 추천하는지 명확한 근거 제공
- **점수 분석**: 각 항목별 상세한 점수 분해
- **대안 추천**: 1순위 외 2-5순위 축제도 제시

### 4. 실시간 축제 정보
- **TourAPI 연동**: 공공데이터포털의 최신 축제 정보
- **자동 데이터 수집**: 정기적인 축제 정보 업데이트
- **지역별 필터링**: 호남 지역(전북, 전남, 광주) 중심

## 🛠️ 기술 스택

- **Backend Framework**: FastAPI
- **Database ORM**: SQLAlchemy
- **Database**: MySQL (네이버 클라우드)
- **AI/LLM**: LangChain + ClovaX
- **Authentication**: JWT + bcrypt
- **Data Validation**: Pydantic
- **Deployment**: 네이버 클라우드 VPC
- **Service Management**: systemd

## 📊 API 사용 예시

### 1. 봇 인사말 요청
```bash
curl -X POST "http://localhost:8000/bot/greeting" \
  -H "Content-Type: application/json" \
  -d '{
    "travel_period": "10월",
    "companion_type": "부모님 동반 가족"
  }'
```

### 2. XAI 최종 추천
```bash
curl -X POST "http://localhost:8000/bot/finalize" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "your-session-id"
  }'
```

## 🔍 문제 해결

### 일반적인 문제들
1. **Import 에러**: 모든 필요한 모델이 `models.py`에 정의되어 있는지 확인
2. **데이터베이스 연결**: `.env` 파일의 `DATABASE_URL` 설정 확인
3. **API 키**: `TOUR_API_KEY`와 `CLOVASTUDIO_API_KEY` 설정 확인

### 로그 확인
```bash
# 실시간 로그 확인
sudo journalctl -u namdo-bot -f

# 최근 로그 확인
sudo journalctl -u namdo-bot --no-pager -n 100
```

## 📈 성능 최적화

- **데이터베이스 인덱스**: 자주 조회되는 필드에 인덱스 설정
- **LLM 응답 캐싱**: 동일한 질문에 대한 응답 캐싱
- **비동기 처리**: FastAPI의 비동기 특성 활용

## 🔮 향후 계획

- [ ] **벡터 검색**: FAISS를 활용한 의미 기반 축제 검색
- [ ] **사용자 피드백**: 추천 품질 개선을 위한 피드백 시스템
- [ ] **모바일 앱**: React Native 기반 모바일 애플리케이션
- [ ] **실시간 알림**: 새로운 축제 정보 실시간 알림

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 문의

프로젝트에 대한 문의사항이 있으시면 이슈를 생성해 주세요.

---

**🎉 남도봇과 함께 호남 지역의 멋진 축제를 발견해보세요!**
