# 🎯 남도봇 축제 추천 시스템 (Namdo Bot Festival Recommendation System)

## 📋 프로젝트 개요

AI 기반 멀티턴 대화형 남도 축제 추천 시스템으로, LangChain과 ClovaX LLM을 활용하여 사용자 맞춤형 축제를 추천합니다. 

### 🎯 핵심 목표
- **지능형 추천**: 사용자 선호도 기반 AI 축제 추천
- **대화형 인터페이스**: 자연스러운 대화를 통한 정보 수집
- **XAI 제공**: 추천 이유와 근거를 명확하게 설명
- **실시간 데이터**: TourAPI 연동으로 최신 축제 정보 제공
- **사용자 맞춤**: 여행 시기, 동반자, 선호도 등 개인화된 추천

### 🌍 서비스 대상 지역
- **전북특별자치도**: 전주, 군산, 익산, 정읍, 남원, 김제, 완주, 진안, 무주, 장수, 임실, 순창, 고창, 부안
- **전남**: 목포, 여수, 순천, 나주, 광양, 담양, 곡성, 구례, 고흥, 보성, 화순, 장흥, 강진, 해남, 영암, 무안, 함평, 영광, 장성, 완도, 진도
- **광주광역시**: 동구, 서구, 남구, 북구, 광산구

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
Flova/
├── README.md
├── backend/
│   ├── actual/                    # 🚀 서비스 백엔드 (운영)
│   │   ├── namdo_bot.py           # FastAPI 앱 진입점
│   │   ├── crud.py                # DB CRUD
│   │   ├── core/
│   │   │   ├── database.py        # SQLAlchemy 모델·세션
│   │   │   └── auth.py           # JWT 인증
│   │   ├── schemas/
│   │   │   └── models.py         # Pydantic 요청/응답 모델
│   │   ├── services/
│   │   │   ├── tour_api.py        # 관광공사 API 클라이언트
│   │   │   └── festival_service.py  # 축제 수집·추천 서비스
│   │   ├── scripts/
│   │   │   └── honam_festivals_to_csv.py  # 축제 → CSV 수집
│   │   ├── requirements.txt
│   │   ├── deploy.sh
│   │   └── env_example.txt
│   └── example/                   # 예제·테스트
│       ├── LLM_RAG_example/
│       ├── check_db.py
│       └── test_mysql_connection.py
└── llm_relevant/                   # LLM·RAG 실험·예제
    ├── data/                       # CSV 등 데이터
    │   ├── honam_festivals_base.csv
    │   ├── honam_festivals_common.csv
    │   └── honam_festivals_intro.csv
    ├── rag/
    │   └── langchain_RAG.py        # LangChain RAG (CSV → FAISS)
    ├── examples/                   # 단계별 예제
    │   ├── 01_llm.py
    │   ├── 02_.py
    │   ├── 03_Langchain_RAG.py
    │   ├── 04_fastAPI.py
    │   ├── 05_chatbot.py
    │   └── 원래_03.py
    ├── templates/
    │   └── index.html
    ├── scripts/
    │   ├── honam_festivals_to_csv.py
    │   └── tour_api.py
    ├── requirements.txt
    ├── .gitignore
    └── LICENSE
```

- **백엔드 실행**: `cd backend/actual` 후 `python namdo_bot.py` (또는 uvicorn)
- **CSV 수집(백엔드)**: `cd backend/actual` 후 `python scripts/honam_festivals_to_csv.py`
- **RAG 실행**: `cd llm_relevant` 후 `python rag/langchain_RAG.py` (데이터는 `llm_relevant/data/` 사용)

## 🗄️ 데이터베이스 스키마 상세

### 📊 전체 테이블 구조

```sql
-- 데이터베이스 생성
CREATE DATABASE IF NOT EXISTS flova CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE flova;

-- 사용자 테이블
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '사용자 고유 ID',
    username VARCHAR(255) UNIQUE NOT NULL COMMENT '사용자명 (고유)',
    email VARCHAR(255) UNIQUE NOT NULL COMMENT '이메일 주소 (고유)',
    full_name VARCHAR(255) NOT NULL COMMENT '실명',
    hashed_password VARCHAR(255) NOT NULL COMMENT '암호화된 비밀번호',
    profile_picture VARCHAR(255) COMMENT '프로필 사진 URL',
    is_active BOOLEAN DEFAULT TRUE COMMENT '계정 활성 상태',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '계정 생성 시간',
    updated_at TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '정보 수정 시간',
    
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_created_at (created_at)
) COMMENT '사용자 계정 정보';

-- 대화 세션 테이블
CREATE TABLE conversations (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '대화 세션 고유 ID',
    user_id INT NOT NULL COMMENT '사용자 ID (외래키)',
    session_id VARCHAR(255) UNIQUE NOT NULL COMMENT '세션 식별자 (UUID)',
    travel_period VARCHAR(50) COMMENT '여행 시기 (예: 10월, 봄, 여름)',
    companion_type VARCHAR(100) COMMENT '동반자 유형 (예: 혼자, 연인, 가족)',
    has_pets BOOLEAN DEFAULT FALSE COMMENT '반려동물 동반 여부',
    child_age_group VARCHAR(50) COMMENT '아동 연령대 (예: 유아, 초등학생)',
    energy_preference VARCHAR(100) COMMENT '선호 분위기 (예: 활기찬, 여유로운)',
    interest_focus VARCHAR(100) COMMENT '핵심 관심사 (예: 음식, 문화, 자연)',
    additional_requirements TEXT COMMENT '추가 고려사항 (예: 걷기 최소화, 휴식공간)',
    phase VARCHAR(50) DEFAULT 'initial' COMMENT '대화 단계 (initial, energy_preference, interest_focus, final)',
    status VARCHAR(50) DEFAULT 'active' COMMENT '세션 상태 (active, completed, expired)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '세션 생성 시간',
    updated_at TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '세션 수정 시간',
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_session_id (session_id),
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at),
    INDEX idx_status (status)
) COMMENT '사용자 대화 세션 정보';

-- 축제 기본 정보 테이블
CREATE TABLE festivals (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '축제 고유 ID',
    contentid VARCHAR(50) UNIQUE NOT NULL COMMENT 'TourAPI 콘텐츠 ID',
    title VARCHAR(500) NOT NULL COMMENT '축제 제목',
    contenttypeid VARCHAR(50) COMMENT '콘텐츠 타입 ID (TourAPI)',
    addr1 VARCHAR(500) COMMENT '주소 (시도명)',
    addr2 VARCHAR(500) COMMENT '상세 주소',
    start_date VARCHAR(20) COMMENT '축제 시작일 (YYYYMMDD)',
    end_date VARCHAR(20) COMMENT '축제 종료일 (YYYYMMDD)',
    image VARCHAR(1000) COMMENT '대표 이미지 URL',
    progresstype VARCHAR(100) COMMENT '진행 유형 (예: 진행중, 예정)',
    festivaltype VARCHAR(100) COMMENT '축제 유형 (예: 문화축제, 음식축제)',
    tel VARCHAR(100) COMMENT '연락처',
    region VARCHAR(100) COMMENT '지역 (전북, 전남, 광주)',
    mapx VARCHAR(50) COMMENT '경도 (X좌표)',
    mapy VARCHAR(50) COMMENT '위도 (Y좌표)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '데이터 생성 시간',
    
    INDEX idx_contentid (contentid),
    INDEX idx_region (region),
    INDEX idx_start_date (start_date),
    INDEX idx_end_date (end_date),
    INDEX idx_festivaltype (festivaltype),
    INDEX idx_created_at (created_at)
) COMMENT '축제 기본 정보';

-- 축제 상세 정보 테이블
CREATE TABLE festival_details (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '상세 정보 고유 ID',
    contentid VARCHAR(50) NOT NULL COMMENT '축제 ID (외래키)',
    title VARCHAR(500) NOT NULL COMMENT '축제 제목',
    createdtime VARCHAR(20) COMMENT 'TourAPI 생성 시간',
    modifiedtime VARCHAR(20) COMMENT 'TourAPI 수정 시간',
    tel VARCHAR(100) COMMENT '연락처',
    telname VARCHAR(100) COMMENT '연락처 담당자명',
    homepage VARCHAR(1000) COMMENT '홈페이지 URL',
    firstimage VARCHAR(1000) COMMENT '첫 번째 이미지 URL',
    firstimage2 VARCHAR(1000) COMMENT '두 번째 이미지 URL',
    addr1 VARCHAR(500) COMMENT '주소 (시도명)',
    addr2 VARCHAR(500) COMMENT '상세 주소',
    mapx VARCHAR(50) COMMENT '경도 (X좌표)',
    mapy VARCHAR(50) COMMENT '위도 (Y좌표)',
    mlevel VARCHAR(50) COMMENT '지도 레벨',
    overview TEXT COMMENT '축제 개요 및 설명',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '데이터 생성 시간',
    
    FOREIGN KEY (contentid) REFERENCES festivals(contentid) ON DELETE CASCADE,
    INDEX idx_contentid (contentid),
    INDEX idx_created_at (created_at)
) COMMENT '축제 상세 정보';

-- 축제 소개 정보 테이블
CREATE TABLE festival_intros (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '소개 정보 고유 ID',
    contentid VARCHAR(50) NOT NULL COMMENT '축제 ID (외래키)',
    sponsor1 VARCHAR(200) COMMENT '주최자 1',
    sponsor1tel VARCHAR(100) COMMENT '주최자 1 연락처',
    sponsor2 VARCHAR(200) COMMENT '주최자 2',
    sponsor2tel VARCHAR(100) COMMENT '주최자 2 연락처',
    eventenddate VARCHAR(20) COMMENT '행사 종료일',
    playtime VARCHAR(200) COMMENT '관람 소요 시간',
    eventplace VARCHAR(500) COMMENT '행사 장소',
    eventstartdate VARCHAR(20) COMMENT '행사 시작일',
    usetimefestival VARCHAR(500) COMMENT '축제 이용 시간',
    progresstype VARCHAR(100) COMMENT '진행 유형',
    festivaltype VARCHAR(100) COMMENT '축제 유형',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '데이터 생성 시간',
    
    FOREIGN KEY (contentid) REFERENCES festivals(contentid) ON DELETE CASCADE,
    INDEX idx_contentid (contentid),
    INDEX idx_eventstartdate (eventstartdate),
    INDEX idx_eventenddate (eventenddate),
    INDEX idx_created_at (created_at)
) COMMENT '축제 소개 및 행사 정보';

-- 반려동물 정보 테이블
CREATE TABLE pet_infos (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '반려동물 정보 고유 ID',
    contentid VARCHAR(50) NOT NULL COMMENT '축제 ID (외래키)',
    acmpyPsblCpam VARCHAR(200) COMMENT '동반 가능 동물',
    relaRntlPrdlst VARCHAR(500) COMMENT '관련 임대 상품 목록',
    acmpyNeedMtr VARCHAR(500) COMMENT '동반 시 필요 사항',
    etcAcmpyInfo TEXT COMMENT '기타 동반 정보',
    relaPurcPrdlst VARCHAR(500) COMMENT '관련 구매 상품 목록',
    relaAcdntRiskMtr VARCHAR(500) COMMENT '관련 사고 위험 요소',
    acmpyTypeCd VARCHAR(50) COMMENT '동반 유형 코드',
    relaPosesFclty VARCHAR(500) COMMENT '관련 편의 시설',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '데이터 생성 시간',
    
    FOREIGN KEY (contentid) REFERENCES festivals(contentid) ON DELETE CASCADE,
    INDEX idx_contentid (contentid),
    INDEX idx_acmpyTypeCd (acmpyTypeCd),
    INDEX idx_created_at (created_at)
) COMMENT '반려동물 동반 관련 정보';
```

### 🔗 테이블 관계도

```
users (사용자)
    │
    ├── conversations (대화 세션) ── 1:N 관계
    │
festivals (축제 기본 정보)
    │
    ├── festival_details (축제 상세 정보) ── 1:1 관계
    ├── festival_intros (축제 소개 정보) ── 1:1 관계
    └── pet_infos (반려동물 정보) ── 1:1 관계
```

### 📋 컬럼 상세 설명

#### Users 테이블
| 컬럼명 | 타입 | 제약조건 | 설명 | 예시값 |
|--------|------|----------|------|--------|
| id | INT | PK, AUTO_INCREMENT | 사용자 고유 ID | 1, 2, 3... |
| username | VARCHAR(255) | UNIQUE, NOT NULL | 사용자명 (로그인용) | "user123", "traveler" |
| email | VARCHAR(255) | UNIQUE, NOT NULL | 이메일 주소 | "user@example.com" |
| full_name | VARCHAR(255) | NOT NULL | 사용자 실명 | "홍길동", "김철수" |
| hashed_password | VARCHAR(255) | NOT NULL | bcrypt 암호화된 비밀번호 | "$2b$12$..." |
| profile_picture | VARCHAR(255) | NULL | 프로필 사진 URL | "https://..." |
| is_active | BOOLEAN | DEFAULT TRUE | 계정 활성 상태 | true, false |
| created_at | TIMESTAMP | DEFAULT NOW | 계정 생성 시간 | "2025-08-30 10:00:00" |
| updated_at | TIMESTAMP | ON UPDATE | 정보 수정 시간 | "2025-08-30 10:30:00" |

#### Conversations 테이블
| 컬럼명 | 타입 | 제약조건 | 설명 | 예시값 |
|--------|------|----------|------|--------|
| id | INT | PK, AUTO_INCREMENT | 대화 세션 고유 ID | 1, 2, 3... |
| user_id | INT | FK, NOT NULL | 사용자 ID | 1, 2, 3... |
| session_id | VARCHAR(255) | UNIQUE, NOT NULL | 세션 식별자 (UUID) | "550e8400-..." |
| travel_period | VARCHAR(50) | NULL | 여행 시기 | "10월", "봄", "여름" |
| companion_type | VARCHAR(100) | NULL | 동반자 유형 | "혼자", "연인", "가족" |
| has_pets | BOOLEAN | DEFAULT FALSE | 반려동물 동반 여부 | true, false |
| child_age_group | VARCHAR(50) | NULL | 아동 연령대 | "유아", "초등학생" |
| energy_preference | VARCHAR(100) | NULL | 선호 분위기 | "활기찬", "여유로운" |
| interest_focus | VARCHAR(100) | NULL | 핵심 관심사 | "음식", "문화", "자연" |
| additional_requirements | TEXT | NULL | 추가 고려사항 | "걷기 최소화" |
| phase | VARCHAR(50) | DEFAULT 'initial' | 대화 단계 | "initial", "final" |
| status | VARCHAR(50) | DEFAULT 'active' | 세션 상태 | "active", "completed" |

#### Festivals 테이블
| 컬럼명 | 타입 | 제약조건 | 설명 | 예시값 |
|--------|------|----------|------|--------|
| id | INT | PK, AUTO_INCREMENT | 축제 고유 ID | 1, 2, 3... |
| contentid | VARCHAR(50) | UNIQUE, NOT NULL | TourAPI 콘텐츠 ID | "1234567" |
| title | VARCHAR(500) | NOT NULL | 축제 제목 | "순창장류축제" |
| contenttypeid | VARCHAR(50) | NULL | 콘텐츠 타입 ID | "15" |
| addr1 | VARCHAR(500) | NULL | 주소 (시도명) | "전북특별자치도" |
| addr2 | VARCHAR(500) | NULL | 상세 주소 | "순창군 순창읍" |
| start_date | VARCHAR(20) | NULL | 축제 시작일 | "20241001" |
| end_date | VARCHAR(20) | NULL | 축제 종료일 | "20241003" |
| image | VARCHAR(1000) | NULL | 대표 이미지 URL | "https://..." |
| progresstype | VARCHAR(100) | NULL | 진행 유형 | "진행중", "예정" |
| festivaltype | VARCHAR(100) | NULL | 축제 유형 | "문화축제", "음식축제" |
| tel | VARCHAR(100) | NULL | 연락처 | "063-123-4567" |
| region | VARCHAR(100) | NULL | 지역 | "전북", "전남", "광주" |

### 🗂️ 인덱스 전략

#### 성능 최적화를 위한 인덱스
```sql
-- 자주 조회되는 필드에 인덱스 생성
CREATE INDEX idx_festivals_region_date ON festivals(region, start_date, end_date);
CREATE INDEX idx_festivals_type_region ON festivals(festivaltype, region);
CREATE INDEX idx_conversations_user_status ON conversations(user_id, status);
CREATE INDEX idx_conversations_session_phase ON conversations(session_id, phase);

-- 복합 인덱스로 검색 성능 향상
CREATE INDEX idx_festivals_search ON festivals(region, festivaltype, start_date);
CREATE INDEX idx_conversations_user_created ON conversations(user_id, created_at);
```

### 🔄 데이터 무결성 제약조건

```sql
-- 외래키 제약조건
ALTER TABLE conversations 
ADD CONSTRAINT fk_conversations_user 
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

ALTER TABLE festival_details 
ADD CONSTRAINT fk_festival_details_festival 
FOREIGN KEY (contentid) REFERENCES festivals(contentid) ON DELETE CASCADE;

ALTER TABLE festival_intros 
ADD CONSTRAINT fk_festival_intros_festival 
FOREIGN KEY (contentid) REFERENCES festivals(contentid) ON DELETE CASCADE;

ALTER TABLE pet_infos 
ADD CONSTRAINT fk_pet_infos_festival 
FOREIGN KEY (contentid) REFERENCES festivals(contentid) ON DELETE CASCADE;

-- 체크 제약조건 (MySQL 8.0+)
ALTER TABLE users 
ADD CONSTRAINT chk_username_length CHECK (LENGTH(username) >= 3 AND LENGTH(username) <= 20);

ALTER TABLE users 
ADD CONSTRAINT chk_password_length CHECK (LENGTH(hashed_password) >= 8);

ALTER TABLE conversations 
ADD CONSTRAINT chk_phase_values CHECK (phase IN ('initial', 'energy_preference', 'interest_focus', 'final'));

ALTER TABLE conversations 
ADD CONSTRAINT chk_status_values CHECK (status IN ('active', 'completed', 'expired'));
```

## 🔌 API 엔드포인트 상세 명세

### 🔐 인증 관련 API

#### POST /auth/register
**회원가입**
- **URL**: `/auth/register`
- **Method**: `POST`
- **Content-Type**: `application/json`
- **인증**: 불필요

**Request Body**:
```json
{
  "username": "string (필수, 3-20자, 영문/숫자/언더스코어)",
  "email": "string (필수, 이메일 형식)",
  "full_name": "string (필수, 2-50자)",
  "password": "string (필수, 8-50자)"
}
```

**Response (201 Created)**:
```json
{
  "id": 1,
  "username": "user123",
  "email": "user@example.com",
  "full_name": "홍길동",
  "profile_picture": null,
  "is_active": true,
  "created_at": "2025-08-30T10:00:00Z"
}
```

**Error Response (400 Bad Request)**:
```json
{
  "detail": "이미 존재하는 사용자명입니다."
}
```

#### POST /auth/login
**로그인**
- **URL**: `/auth/login`
- **Method**: `POST`
- **Content-Type**: `application/json`
- **인증**: 불필요

**Request Body**:
```json
{
  "username": "string (필수)",
  "password": "string (필수)"
}
```

**Response (200 OK)**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "user123",
    "email": "user@example.com",
    "full_name": "홍길동",
    "profile_picture": null,
    "is_active": true
  }
}
```

**Error Response (401 Unauthorized)**:
```json
{
  "detail": "잘못된 사용자명 또는 비밀번호입니다."
}
```

#### GET /users/me
**사용자 정보 조회**
- **URL**: `/users/me`
- **Method**: `GET`
- **인증**: Bearer Token 필요
- **Headers**: `Authorization: Bearer {token}`

**Response (200 OK)**:
```json
{
  "id": 1,
  "username": "user123",
  "email": "user@example.com",
  "full_name": "홍길동",
  "profile_picture": "https://example.com/profile.jpg",
  "is_active": true,
  "created_at": "2025-08-30T10:00:00Z",
  "updated_at": "2025-08-30T10:00:00Z"
}
```

#### PUT /users/me/profile
**프로필 정보 업데이트**
- **URL**: `/users/me/profile`
- **Method**: `PUT`
- **Content-Type**: `application/json`
- **인증**: Bearer Token 필요
- **Headers**: `Authorization: Bearer {token}`

**Request Body**:
```json
{
  "full_name": "string (선택, 2-50자)",
  "profile_picture": "string (선택, URL)"
}
```

**Response (200 OK)**:
```json
{
  "id": 1,
  "username": "user123",
  "email": "user@example.com",
  "full_name": "김철수",
  "profile_picture": "https://example.com/new-profile.jpg",
  "is_active": true,
  "updated_at": "2025-08-30T10:30:00Z"
}
```

### 🤖 봇 관련 API

#### POST /bot/greeting
**봇 인사말 및 첫 번째 질문**
- **URL**: `/bot/greeting`
- **Method**: `POST`
- **Content-Type**: `application/json`
- **인증**: Bearer Token 필요
- **Headers**: `Authorization: Bearer {token}`

**Request Body**:
```json
{
  "travel_period": "string (필수, 예: '10월', '봄', '여름')",
  "companion_type": "string (필수, 예: '혼자', '연인', '친구', '아이 동반 가족', '부모님 동반 가족')"
}
```

**Response (200 OK)**:
```json
{
  "greeting_message": "안녕하세요! 10월에 부모님과 함께하는 호남 여행을 계획하고 계시는군요! 😊",
  "next_question": "이번 여행의 전체적인 분위기는 어떤 느낌을 선호하시나요?",
  "choices": [
    "A: 다양한 볼거리와 체험이 가득한 활기찬 분위기",
    "B: 아름다운 풍경을 보며 즐기는 여유롭고 고즈넉한 분위기"
  ],
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "phase": "energy_preference",
  "status": "active"
}
```

#### POST /bot/finalize
**XAI 기반 최종 추천 및 설명**
- **URL**: `/bot/finalize`
- **Method**: `POST`
- **Content-Type**: `application/json`
- **인증**: Bearer Token 필요
- **Headers**: `Authorization: Bearer {token}`

**Request Body**:
```json
{
  "session_id": "string (필수, UUID)"
}
```

**Response (200 OK)**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_profile": {
    "travel_period": "10월",
    "companion_type": "부모님 동반 가족",
    "energy_preference": "여유로운 분위기",
    "interest_focus": "음식",
    "additional_requirements": "걷기 최소화"
  },
  "recommendation_summary": {
    "total_count": 3,
    "message": "총 3개의 축제를 추천드립니다.",
    "score_range": {
      "highest": 85,
      "lowest": 70
    }
  },
  "top_recommendation": {
    "title": "순창장류축제",
    "region": "전북특별자치도",
    "start_date": "20241001",
    "end_date": "20241003",
    "location": "전북 순창군",
    "score": 85,
    "reasons": ["호남 지역 축제", "계절에 적합", "부모님과 함께하기 좋은 여유로운 분위기"],
    "why_best": "사용자의 모든 조건을 가장 잘 만족하는 축제입니다.",
    "image": "https://example.com/festival1.jpg",
    "tel": "063-123-4567"
  },
  "alternative_recommendations": [
    {
      "rank": 2,
      "title": "남원흥부제",
      "region": "전북특별자치도",
      "start_date": "20241008",
      "end_date": "20241010",
      "location": "전북 남원시",
      "score": 75,
      "reasons": ["호남 지역 축제", "계절에 적합", "음식 중심 축제"],
      "why_alternative": "2순위로 추천하는 이유: 호남 지역 축제, 계절에 적합, 음식 중심 축제",
      "image": "https://example.com/festival2.jpg",
      "tel": "063-234-5678"
    }
  ],
  "score_breakdown": {
    "region_compatibility": 10,
    "season_matching": 15,
    "companion_optimization": 20,
    "interest_matching": 25,
    "accessibility_consideration": 15,
    "total_score": 85
  },
  "recommendation_criteria": {
    "region_priority": "호남 지역 (전북, 전남, 광주)",
    "season_focus": "10월",
    "companion_type": "부모님 동반 가족",
    "interest_focus": "음식",
    "accessibility_focus": "걷기 최소화"
  },
  "reasoning_summary": {
    "message": "AI가 분석한 추천 근거와 점수 계산 과정을 상세히 설명합니다.",
    "suggestions": [
      "추천된 축제의 상세 정보를 확인해보세요",
      "2순위 이하 축제도 고려해보세요",
      "추가 질문이 있으면 언제든 물어보세요"
    ]
  },
  "timestamp": "2025-08-30T10:00:00Z"
}
```

### 🎉 축제 관련 API

#### POST /festivals/collect
**축제 데이터 수집 (관리자용)**
- **URL**: `/festivals/collect`
- **Method**: `POST`
- **Content-Type**: `application/json`
- **인증**: Bearer Token 필요 (관리자 권한)
- **Headers**: `Authorization: Bearer {token}`

**Request Body**:
```json
{
  "region": "string (선택, 예: '전북', '전남', '광주')",
  "force_update": "boolean (선택, 기본값: false)"
}
```

**Response (200 OK)**:
```json
{
  "message": "축제 데이터 수집이 완료되었습니다.",
  "collected_count": 150,
  "updated_count": 25,
  "region": "전북",
  "timestamp": "2025-08-30T10:00:00Z"
}
```

#### GET /festivals/search
**축제 검색 및 필터링**
- **URL**: `/festivals/search`
- **Method**: `GET`
- **인증**: Bearer Token 필요
- **Headers**: `Authorization: Bearer {token}`

**Query Parameters**:
- `region` (선택): 지역 필터 (예: '전북', '전남', '광주')
- `period` (선택): 기간 필터 (예: '202410', '봄', '여름')
- `festival_type` (선택): 축제 유형 (예: '문화축제', '음식축제', '자연축제')
- `has_pet_info` (선택): 반려동물 정보 포함 여부 (true/false)
- `page` (선택): 페이지 번호 (기본값: 1)
- `limit` (선택): 페이지당 결과 수 (기본값: 20)

**Response (200 OK)**:
```json
{
  "festivals": [
    {
      "id": 1,
      "contentid": "1234567",
      "title": "순창장류축제",
      "region": "전북",
      "start_date": "20241001",
      "end_date": "20241003",
      "image": "https://example.com/festival1.jpg",
      "festivaltype": "음식축제",
      "addr1": "전북 순창군 순창읍"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 150,
    "pages": 8
  }
}
```

#### POST /festivals/recommend
**축제 추천 (직접 요청)**
- **URL**: `/festivals/recommend`
- **Method**: `POST`
- **Content-Type**: `application/json`
- **인증**: Bearer Token 필요
- **Headers**: `Authorization: Bearer {token}`

**Request Body**:
```json
{
  "travel_period": "string (필수)",
  "companion_type": "string (필수)",
  "atmosphere": "string (선택)",
  "core_experience": "string (선택)",
  "additional_considerations": "string (선택)"
}
```

**Response (200 OK)**:
```json
{
  "recommendations": [
    {
      "festival": {
        "id": 1,
        "title": "순창장류축제",
        "region": "전북",
        "start_date": "20241001",
        "end_date": "20241003"
      },
      "score": 85,
      "reasons": ["호남 지역", "계절 적합", "부모님 동반 적합"]
    }
  ],
  "total_count": 3
}
```

### 🏥 시스템 관련 API

#### GET /
**루트 엔드포인트**
- **URL**: `/`
- **Method**: `GET`
- **인증**: 불필요

**Response (200 OK)**:
```json
{
  "message": "남도봇 축제 추천 시스템에 오신 것을 환영합니다!",
  "version": "1.0.0",
  "status": "running",
  "timestamp": "2025-08-30T10:00:00Z"
}
```

#### GET /health
**헬스 체크**
- **URL**: `/health`
- **Method**: `GET`
- **인증**: 불필요

**Response (200 OK)**:
```json
{
  "message": "서비스가 정상적으로 작동 중입니다",
  "status": "healthy",
  "timestamp": "2025-08-30T10:00:00Z",
  "version": "1.0.0",
  "database": "connected",
  "llm_service": "available"
}
```

## 🚀 배포 방법 상세 가이드

### 1. 🏗️ 사전 준비 사항

#### 네이버 클라우드 VPC 서버 준비
- **서버 사양**: 최소 2GB RAM, 20GB SSD
- **OS**: Ubuntu 20.04 LTS 이상 또는 Rocky Linux 8+
- **Python**: Python 3.8 이상
- **방화벽**: 22번(SSH), 8000번(API) 포트 개방

#### MySQL 데이터베이스 설정
- **데이터베이스 엔진**: MySQL 8.0 이상
- **문자셋**: utf8mb4
- **사용자 권한**: DDL, DML 권한 필요
- **네트워크**: VPC 내부 접근 가능

#### SSH 접근 권한
- **인증 방식**: 비밀번호 또는 SSH 키
- **사용자**: root 또는 sudo 권한이 있는 사용자
- **포트**: 22번 포트

### 2. 🔧 배포 실행 단계

#### 2-1. 로컬 환경 준비
```bash
# 프로젝트 디렉토리로 이동
cd backend/actual

# 배포 스크립트 실행 권한 확인
ls -la deploy.sh

# Windows 환경에서 실행 (Git Bash 또는 WSL 사용)
bash deploy.sh
```

#### 2-2. 배포 스크립트 실행 과정
```bash
🚀 남도봇 축제 추천 시스템 VPC 배포 시작...

[STEP] 1. VPC 배포 사전 체크
[STEP] 2. 로컬 빌드 및 패키징
[STEP] 3. VPC 서버 연결 테스트
[STEP] 4. VPC 서버에 프로젝트 디렉토리 생성
[STEP] 5. 파일 업로드 중...
[STEP] 6. VPC 서버에서 Python 환경 설정
[STEP] 7. VPC 환경 변수 설정
[STEP] 8. systemd 서비스 파일 생성
[STEP] 9. VPC 서비스 활성화 및 시작
[STEP] 10. VPC 서비스 상태 확인
[STEP] 11. VPC 보안 설정
[STEP] 12. VPC 배포 완료!
```

#### 2-3. 배포 후 확인 명령어
```bash
# 서비스 상태 확인
sudo systemctl status namdo-bot

# 서비스 활성화 상태 확인
sudo systemctl is-enabled namdo-bot

# 실시간 로그 확인
sudo journalctl -u namdo-bot -f

# 최근 로그 확인 (최근 100줄)
sudo journalctl -u namdo-bot --no-pager -n 100

# API 헬스 체크
curl http://localhost:8000/health

# API 문서 접근
curl http://localhost:8000/docs

# 포트 사용 상태 확인
sudo netstat -tlnp | grep 8000

# 프로세스 상태 확인
ps aux | grep namdo_bot
```

### 3. 🔄 서비스 관리 명령어

#### 3-1. 서비스 제어
```bash
# 서비스 시작
sudo systemctl start namdo-bot

# 서비스 중지
sudo systemctl stop namdo-bot

# 서비스 재시작
sudo systemctl restart namdo-bot

# 서비스 상태 확인
sudo systemctl status namdo-bot

# 서비스 활성화 (부팅 시 자동 시작)
sudo systemctl enable namdo-bot

# 서비스 비활성화
sudo systemctl disable namdo-bot
```

#### 3-2. 로그 관리
```bash
# 실시간 로그 모니터링
sudo journalctl -u namdo-bot -f

# 특정 시간대 로그 확인
sudo journalctl -u namdo-bot --since "2025-08-30 10:00:00"

# 에러 로그만 확인
sudo journalctl -u namdo-bot -p err

# 로그 파일 크기 확인
sudo journalctl --disk-usage

# 로그 정리 (30일 이전 로그 삭제)
sudo journalctl --vacuum-time=30d
```

### 4. 🐛 문제 해결 가이드

#### 4-1. 서비스 시작 실패 시
```bash
# 상세한 에러 로그 확인
sudo journalctl -u namdo-bot --no-pager -n 50

# Python 가상환경 확인
ls -la /home/root/namdo-bot/venv/

# 의존성 패키지 확인
/home/root/namdo-bot/venv/bin/pip list

# 환경 변수 확인
cat /home/root/namdo-bot/.env

# 데이터베이스 연결 테스트
/home/root/namdo-bot/venv/bin/python -c "
import pymysql
pymysql.connect(
    host='db-37h1g8.vpc-cdb.ntruss.com',
    user='flova_user',
    password='your_password',
    database='flova'
)
"
```

#### 4-2. 네트워크 문제 해결
```bash
# 네트워크 연결 상태 확인
ping db-37h1g8.vpc-cdb.ntruss.com

# 포트 연결 확인
telnet db-37h1g8.vpc-cdb.ntruss.com 3306

# 방화벽 상태 확인
sudo ufw status

# ACG 설정 확인 (네이버 클라우드 콘솔)
# - SSH: 22번 포트
# - HTTP: 8000번 포트
# - MySQL: 3306번 포트
```

#### 4-3. 권한 문제 해결
```bash
# 파일 권한 확인
ls -la /home/root/namdo-bot/

# 서비스 파일 권한 확인
ls -la /etc/systemd/system/namdo-bot.service

# 사용자 권한 확인
id root

# Python 가상환경 권한 확인
ls -la /home/root/namdo-bot/venv/bin/python
```

### 5. 📊 모니터링 및 유지보수

#### 5-1. 성능 모니터링
```bash
# CPU 및 메모리 사용량 확인
htop

# 디스크 사용량 확인
df -h

# 네트워크 연결 상태 확인
ss -tuln

# 프로세스 리소스 사용량 확인
ps aux --sort=-%cpu | head -10
```

#### 5-2. 백업 및 복구
```bash
# 데이터베이스 백업
mysqldump -h db-37h1g8.vpc-cdb.ntruss.com -u flova_user -p flova > backup_$(date +%Y%m%d).sql

# 애플리케이션 코드 백업
tar -czf namdo-bot-backup-$(date +%Y%m%d).tar.gz /home/root/namdo-bot/

# 환경 변수 백업
cp /home/root/namdo-bot/.env /home/root/namdo-bot/.env.backup
```

#### 5-3. 업데이트 및 재배포
```bash
# 코드 업데이트 후 재배포
bash deploy.sh

# 의존성 패키지 업데이트
/home/root/namdo-bot/venv/bin/pip install --upgrade -r requirements.txt

# 서비스 재시작
sudo systemctl restart namdo-bot
```

## ⚙️ 환경 변수 설정 상세

### 📁 .env 파일 생성

프로젝트 루트 디렉토리에 `.env` 파일을 생성하고 다음 변수들을 설정해야 합니다:

```bash
# ========================================
# 데이터베이스 설정
# ========================================
# MySQL 연결 문자열 (네이버 클라우드 VPC)
DATABASE_URL=mysql+pymysql://flova_user:your_password@db-37h1g8.vpc-cdb.ntruss.com:3306/flova?charset=utf8mb4

# 로컬 개발용 (선택사항)
# DATABASE_URL=mysql+pymysql://root:password@localhost:3306/flova?charset=utf8mb4

# ========================================
# 외부 API 키 설정
# ========================================
# 공공데이터포털 TourAPI 키 (필수)
TOUR_API_KEY=your_tour_api_key_here

# 네이버 Clova Studio API 키 (필수)
CLOVASTUDIO_API_KEY=your_clovastudio_api_key_here

# ========================================
# JWT 인증 설정
# ========================================
# JWT 시크릿 키 (필수, 32자 이상 권장)
SECRET_KEY=your_super_secret_key_here_make_it_long_and_random

# JWT 알고리즘 (기본값: HS256)
ALGORITHM=HS256

# 액세스 토큰 만료 시간 (분, 기본값: 30)
ACCESS_TOKEN_EXPIRE_MINUTES=30

# ========================================
# 애플리케이션 설정
# ========================================
# 애플리케이션 환경 (development, production, testing)
ENVIRONMENT=production

# 디버그 모드 (true/false, 기본값: false)
DEBUG=false

# 로그 레벨 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO

# ========================================
# 서버 설정
# ========================================
# 서버 호스트 (기본값: 0.0.0.0)
HOST=0.0.0.0

# 서버 포트 (기본값: 8000)
PORT=8000

# 워커 프로세스 수 (기본값: 1)
WORKERS=1

# ========================================
# 보안 설정
# ========================================
# CORS 허용 도메인 (쉼표로 구분)
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com

# 비밀번호 최소 길이 (기본값: 8)
MIN_PASSWORD_LENGTH=8

# 사용자명 최소/최대 길이
MIN_USERNAME_LENGTH=3
MAX_USERNAME_LENGTH=20

# ========================================
# 축제 데이터 설정
# ========================================
# 축제 데이터 자동 수집 주기 (시간, 기본값: 24)
FESTIVAL_COLLECTION_INTERVAL=24

# 최대 축제 데이터 수집 개수 (기본값: 1000)
MAX_FESTIVAL_COUNT=1000

# ========================================
# LLM 설정
# ========================================
# ClovaX 모델명 (기본값: clova-x-1-5b)
CLOVAX_MODEL_NAME=clova-x-1-5b

# LLM 응답 최대 토큰 수 (기본값: 2048)
MAX_TOKENS=2048

# LLM 응답 온도 (0.0-1.0, 기본값: 0.7)
TEMPERATURE=0.7
```

### 🔑 API 키 발급 방법

#### 1. TourAPI (공공데이터포털)
1. [공공데이터포털](https://www.data.go.kr/) 접속
2. 회원가입 및 로그인
3. "TourAPI" 검색
4. "한국관광공사_국문 관광정보 서비스" 신청
5. 승인 후 API 키 발급
6. `.env` 파일의 `TOUR_API_KEY`에 입력

#### 2. Clova Studio API (네이버)
1. [네이버 클라우드 플랫폼](https://www.ncloud.com/) 접속
2. 회원가입 및 로그인
3. "AI·NAVER API" → "Clova Studio" 선택
4. "Clova X" 모델 신청
5. 승인 후 API 키 발급
6. `.env` 파일의 `CLOVASTUDIO_API_KEY`에 입력

### 🔒 보안 설정 가이드

#### 1. JWT 시크릿 키 생성
```bash
# Python을 사용한 안전한 시크릿 키 생성
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# 또는 OpenSSL 사용
openssl rand -base64 32
```

#### 2. 환경 변수 검증
```bash
# .env 파일 권한 설정 (Linux/Mac)
chmod 600 .env

# .env 파일 내용 확인 (비밀번호 제외)
grep -v PASSWORD .env

# 환경 변수 로드 테스트
python3 -c "from dotenv import load_dotenv; load_dotenv(); import os; print('DATABASE_URL:', os.getenv('DATABASE_URL')[:50] + '...')"
```

### 🌍 환경별 설정

#### 개발 환경 (.env.development)
```bash
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/flova_dev?charset=utf8mb4
```

#### 테스트 환경 (.env.testing)
```bash
ENVIRONMENT=testing
DEBUG=false
LOG_LEVEL=INFO
DATABASE_URL=mysql+pymysql://test_user:test_pass@localhost:3306/flova_test?charset=utf8mb4
```

#### 프로덕션 환경 (.env.production)
```bash
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING
DATABASE_URL=mysql+pymysql://flova_user:prod_password@db-37h1g8.vpc-cdb.ntruss.com:3306/flova?charset=utf8mb4
```

### 📋 환경 변수 검증 스크립트

```bash
#!/bin/bash
# check_env.sh

echo "🔍 환경 변수 검증 시작..."

# 필수 환경 변수 목록
required_vars=(
    "DATABASE_URL"
    "TOUR_API_KEY"
    "CLOVASTUDIO_API_KEY"
    "SECRET_KEY"
)

# 각 필수 변수 검증
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ $var 환경 변수가 설정되지 않았습니다."
        exit 1
    else
        echo "✅ $var: ${!var:0:20}..."
    fi
done

# 데이터베이스 연결 테스트
echo "🔌 데이터베이스 연결 테스트..."
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()
import pymysql

try:
    conn = pymysql.connect(
        host=os.getenv('DATABASE_URL').split('@')[1].split(':')[0],
        user=os.getenv('DATABASE_URL').split('://')[1].split(':')[0],
        password=os.getenv('DATABASE_URL').split(':')[2].split('@')[0],
        database=os.getenv('DATABASE_URL').split('/')[-1].split('?')[0],
        port=3306
    )
    print('✅ 데이터베이스 연결 성공!')
    conn.close()
except Exception as e:
    print(f'❌ 데이터베이스 연결 실패: {e}')
    exit(1)
"

echo "🎉 모든 환경 변수 검증 완료!"
```

## 🔧 주요 기능 상세

### 1. 🤖 AI 기반 축제 추천 시스템

#### LangChain RAG (Retrieval-Augmented Generation) 시스템
- **벡터 기반 검색**: FAISS를 활용한 의미 기반 축제 검색
- **컨텍스트 강화**: 사용자 선호도와 축제 정보를 결합한 지능형 추천
- **동적 프롬프트**: 사용자 응답에 따른 적응형 질문 생성

#### ClovaX LLM 통합
- **모델**: 네이버의 최신 대규모 언어 모델 (Clova X 1.5B)
- **한국어 최적화**: 한국어 축제 정보와 사용자 입력에 특화된 처리
- **응답 품질**: 자연스러운 한국어 대화와 정확한 추천 결과

#### 구조화된 JSON 응답
- **PydanticOutputParser**: LLM 응답을 일관된 JSON 형태로 변환
- **스키마 검증**: 응답 데이터의 유효성 자동 검증
- **에러 처리**: 파싱 실패 시 fallback 응답 제공

### 2. 💬 멀티턴 대화 시스템

#### 대화 단계별 정보 수집
```
Phase 1: Initial (초기 정보)
├── 여행 시기 선택
└── 동반자 유형 선택

Phase 2: Energy Preference (분위기 선호도)
├── 활기찬 체험형 vs 여유로운 감상형
└── 사용자 에너지 레벨 파악

Phase 3: Interest Focus (핵심 관심사)
├── 자연/풍경, 음식/맛집, 문화/역사
└── 여행의 주요 목적 파악

Phase 4: Additional Requirements (추가 요구사항)
├── 접근성, 편의시설, 특별 고려사항
└── 숨겨진 니즈 발굴
```

#### 대화 세션 관리
- **UUID 기반 세션**: 고유한 세션 식별자로 대화 추적
- **상태 저장**: 각 단계별 사용자 응답 데이터 저장
- **세션 복구**: 중단된 대화 재개 가능
- **자동 만료**: 장기간 미사용 세션 자동 정리

#### 사용자 프로필 빌딩
- **선호도 분석**: 대화 내용 기반 사용자 취향 분석
- **맥락 이해**: 이전 대화 내용을 고려한 연속성 있는 질문
- **개인화**: 사용자별 맞춤형 추천 알고리즘 적용

### 3. 🔍 XAI (Explainable AI) 시스템

#### 추천 근거 상세 분석
```json
{
  "score_breakdown": {
    "region_compatibility": 10,      // 호남 지역 우선 (+10점)
    "season_matching": 15,           // 계절 적합성 (+15점)
    "companion_optimization": 20,    // 동반자 최적화 (+20점)
    "interest_matching": 25,         // 관심사 매칭 (+25점)
    "accessibility_consideration": 15, // 접근성 고려 (+15점)
    "total_score": 85                // 총점
  }
}
```

#### 점수 계산 알고리즘
- **지역 가중치**: 호남 지역 축제 우선 배점
- **계절 매칭**: 여행 시기와 축제 기간의 일치도
- **동반자 최적화**: 연령대별, 그룹별 적합성
- **관심사 매칭**: 핵심 관심사와 축제 특성의 일치도
- **접근성 고려**: 이동 편의성, 휴식공간 등

#### 대안 추천 시스템
- **1순위**: 최고 점수 축제 (사용자 조건 최적 만족)
- **2-3순위**: 높은 점수 축제 (특정 조건에서 우수)
- **4-5순위**: 보완적 축제 (다양한 옵션 제공)

### 4. 🌐 실시간 축제 정보 시스템

#### TourAPI 연동
- **데이터 소스**: 공공데이터포털 한국관광공사 API
- **실시간 업데이트**: 최신 축제 정보 자동 수집
- **데이터 품질**: 공식 데이터로 신뢰성 보장
- **API 제한**: 일일 요청 한도 내 최적화된 수집

#### 자동 데이터 수집
- **스케줄링**: 24시간마다 자동 축제 정보 업데이트
- **증분 업데이트**: 변경된 정보만 선택적 업데이트
- **에러 처리**: API 오류 시 재시도 및 로깅
- **데이터 검증**: 수집된 데이터의 유효성 검증

#### 지역별 필터링
- **전북특별자치도**: 14개 시군 (전주, 군산, 익산 등)
- **전남**: 22개 시군 (목포, 여수, 순천 등)
- **광주광역시**: 5개 구 (동구, 서구, 남구, 북구, 광산구)

### 5. 🔐 보안 및 인증 시스템

#### JWT 기반 인증
- **토큰 기반**: Stateless 인증으로 서버 부하 최소화
- **자동 갱신**: 토큰 만료 시 자동 재인증
- **보안 강화**: bcrypt를 통한 비밀번호 암호화

#### 사용자 권한 관리
- **일반 사용자**: 축제 검색, 추천, 대화 기능
- **관리자**: 축제 데이터 수집, 시스템 관리
- **권한 분리**: 역할별 접근 제어

### 6. 📊 데이터 분석 및 인사이트

#### 사용자 행동 분석
- **추천 패턴**: 사용자별 선호 축제 유형 분석
- **대화 패턴**: 질문-응답 패턴 분석
- **사용 통계**: API 사용량, 인기 기능 분석

#### 축제 트렌드 분석
- **계절별 인기**: 월별, 계절별 인기 축제 분석
- **지역별 선호도**: 지역별 축제 선호도 분석
- **유형별 분포**: 축제 유형별 분포 및 트렌드

## 🛠️ 기술 스택 상세

### 🚀 Backend Framework
- **FastAPI 0.116.1**: 현대적이고 빠른 Python 웹 프레임워크
  - **비동기 지원**: ASGI 기반 고성능 비동기 처리
  - **자동 문서화**: Swagger UI와 ReDoc 자동 생성
  - **타입 힌트**: Python 타입 힌트를 활용한 자동 검증
  - **OpenAPI 표준**: 표준 API 명세 자동 생성

### 🗄️ Database & ORM
- **SQLAlchemy 2.0.43**: Python 최고의 ORM
  - **비동기 지원**: async/await 기반 비동기 데이터베이스 작업
  - **마이그레이션**: Alembic을 통한 스키마 버전 관리
  - **연결 풀링**: 효율적인 데이터베이스 연결 관리
- **MySQL 8.0.42**: 네이버 클라우드 VPC 데이터베이스
  - **고가용성**: Master-Slave 구성으로 안정성 보장
  - **성능 최적화**: 인덱스 및 쿼리 최적화
  - **문자셋**: utf8mb4로 이모지 및 특수문자 완벽 지원

### 🤖 AI/LLM Integration
- **LangChain 0.3.27**: LLM 애플리케이션 개발 프레임워크
  - **RAG 시스템**: Retrieval-Augmented Generation 구현
  - **프롬프트 관리**: 체인 기반 프롬프트 구성
  - **메모리 관리**: 대화 컨텍스트 유지
- **Clova Studio 0.1.1**: 네이버 AI 모델 통합
  - **Clova X 1.5B**: 한국어 특화 대규모 언어 모델
  - **한국어 최적화**: 한국어 축제 정보 처리에 특화
  - **API 통합**: 네이버 클라우드 플랫폼 연동

### 🔐 Authentication & Security
- **JWT (PyJWT 3.5.0)**: JSON Web Token 기반 인증
  - **Stateless**: 서버 부하 최소화
  - **자동 갱신**: 토큰 만료 시 자동 재인증
  - **보안 강화**: HS256 알고리즘 사용
- **bcrypt 4.3.0**: 비밀번호 암호화
  - **솔트 자동 생성**: 보안성 향상
  - **적응형 해싱**: 컴퓨팅 파워에 따른 보안 강화

### 📊 Data Processing & Validation
- **Pydantic 2.11.7**: 데이터 검증 및 직렬화
  - **스키마 검증**: 런타임 데이터 유효성 검사
  - **자동 변환**: JSON ↔ Python 객체 자동 변환
  - **에러 처리**: 상세한 검증 에러 메시지
- **FAISS 1.12.0**: 벡터 유사도 검색
  - **고성능 검색**: 대용량 벡터 데이터 빠른 검색
  - **메모리 최적화**: 효율적인 메모리 사용

### 🌐 External API Integration
- **TourAPI**: 공공데이터포털 한국관광공사 API
  - **실시간 데이터**: 최신 축제 정보 자동 수집
  - **데이터 품질**: 공식 데이터로 신뢰성 보장
- **Requests 2.32.5**: HTTP 클라이언트 라이브러리
  - **세션 관리**: 효율적인 HTTP 연결 재사용
  - **에러 처리**: 네트워크 오류 자동 재시도

### 🚀 Deployment & Infrastructure
- **네이버 클라우드 VPC**: 가상 프라이빗 클라우드
  - **네트워크 격리**: 보안성 향상
  - **자동 스케일링**: 트래픽에 따른 자동 확장
- **systemd**: Linux 서비스 관리
  - **자동 시작**: 부팅 시 자동 서비스 시작
  - **모니터링**: 서비스 상태 실시간 모니터링
  - **로그 관리**: 통합된 로그 수집 및 관리

### 📦 Development Tools
- **Python 3.8+**: 메인 프로그래밍 언어
- **uvicorn 0.35.0**: ASGI 서버
- **python-dotenv 1.1.1**: 환경 변수 관리
- **python-multipart 0.0.20**: 파일 업로드 처리

### 🔧 Monitoring & Logging
- **로깅 시스템**: Python 내장 logging 모듈
- **에러 추적**: 상세한 에러 로그 및 스택 트레이스
- **성능 모니터링**: API 응답 시간 및 리소스 사용량 추적

### 📱 API Documentation
- **Swagger UI**: `/docs` 엔드포인트로 자동 생성
- **ReDoc**: `/redoc` 엔드포인트로 대안 문서 제공
- **OpenAPI 3.0**: 표준 API 명세 자동 생성

## 📊 API 사용 예시 상세

### 1. 🔐 사용자 인증 플로우

#### 1-1. 회원가입
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "traveler123",
    "email": "traveler@example.com",
    "full_name": "김여행",
    "password": "securepassword123"
  }'
```

**응답 예시**:
```json
{
  "id": 1,
  "username": "traveler123",
  "email": "traveler@example.com",
  "full_name": "김여행",
  "profile_picture": null,
  "is_active": true,
  "created_at": "2025-08-30T10:00:00Z"
}
```

#### 1-2. 로그인
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "traveler123",
    "password": "securepassword123"
  }'
```

**응답 예시**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "traveler123",
    "email": "traveler@example.com",
    "full_name": "김여행"
  }
}
```

### 2. 🤖 봇 대화 플로우

#### 2-1. 봇 인사말 및 첫 질문
```bash
curl -X POST "http://localhost:8000/bot/greeting" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "travel_period": "10월",
    "companion_type": "부모님 동반 가족"
  }'
```

**응답 예시**:
```json
{
  "greeting_message": "안녕하세요! 10월에 부모님과 함께하는 호남 여행을 계획하고 계시는군요! 😊",
  "next_question": "이번 여행의 전체적인 분위기는 어떤 느낌을 선호하시나요?",
  "choices": [
    "A: 다양한 볼거리와 체험이 가득한 활기찬 분위기",
    "B: 아름다운 풍경을 보며 즐기는 여유롭고 고즈넉한 분위기"
  ],
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "phase": "energy_preference",
  "status": "active"
}
```

#### 2-2. 사용자 응답 (에너지 레벨 선택)
```bash
curl -X PUT "http://localhost:8000/bot/conversation/550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "energy_preference": "여유로운 분위기"
  }'
```

#### 2-3. XAI 최종 추천
```bash
curl -X POST "http://localhost:8000/bot/finalize" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

### 3. 🎉 축제 검색 및 추천

#### 3-1. 축제 검색 (필터링)
```bash
curl -X GET "http://localhost:8000/festivals/search?region=전북&festival_type=음식축제&page=1&limit=10" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**응답 예시**:
```json
{
  "festivals": [
    {
      "id": 1,
      "contentid": "1234567",
      "title": "순창장류축제",
      "region": "전북",
      "start_date": "20241001",
      "end_date": "20241003",
      "image": "https://example.com/festival1.jpg",
      "festivaltype": "음식축제",
      "addr1": "전북 순창군 순창읍"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 45,
    "pages": 5
  }
}
```

#### 3-2. 직접 축제 추천
```bash
curl -X POST "http://localhost:8000/festivals/recommend" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "travel_period": "10월",
    "companion_type": "부모님 동반 가족",
    "atmosphere": "여유로운 분위기",
    "core_experience": "음식",
    "additional_considerations": "걷기 최소화"
  }'
```

### 4. 🔧 시스템 관리

#### 4-1. 헬스 체크
```bash
curl -X GET "http://localhost:8000/health"
```

**응답 예시**:
```json
{
  "message": "서비스가 정상적으로 작동 중입니다",
  "status": "healthy",
  "timestamp": "2025-08-30T10:00:00Z",
  "version": "1.0.0",
  "database": "connected",
  "llm_service": "available"
}
```

#### 4-2. 축제 데이터 수집 (관리자용)
```bash
curl -X POST "http://localhost:8000/festivals/collect" \
  -H "Authorization: Bearer ADMIN_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "region": "전북",
    "force_update": false
  }'
```

### 5. 📱 프론트엔드 통합 예시

#### 5-1. React 컴포넌트 예시
```jsx
import React, { useState, useEffect } from 'react';

const FestivalRecommendation = () => {
  const [sessionId, setSessionId] = useState(null);
  const [conversation, setConversation] = useState(null);
  const [recommendations, setRecommendations] = useState(null);

  // 봇 대화 시작
  const startConversation = async (travelPeriod, companionType) => {
    try {
      const response = await fetch('/bot/greeting', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ travel_period: travelPeriod, companion_type: companionType })
      });
      
      const data = await response.json();
      setSessionId(data.session_id);
      setConversation(data);
    } catch (error) {
      console.error('대화 시작 실패:', error);
    }
  };

  // 최종 추천 받기
  const getFinalRecommendations = async () => {
    try {
      const response = await fetch('/bot/finalize', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ session_id: sessionId })
      });
      
      const data = await response.json();
      setRecommendations(data);
    } catch (error) {
      console.error('추천 받기 실패:', error);
    }
  };

  return (
    <div>
      {/* 대화 시작 UI */}
      <button onClick={() => startConversation('10월', '부모님 동반 가족')}>
        부모님과 10월 여행 계획하기
      </button>

      {/* 대화 진행 UI */}
      {conversation && (
        <div>
          <p>{conversation.greeting_message}</p>
          <p>{conversation.next_question}</p>
          {conversation.choices.map((choice, index) => (
            <button key={index} onClick={() => handleChoice(choice)}>
              {choice}
            </button>
          ))}
        </div>
      )}

      {/* 최종 추천 UI */}
      {recommendations && (
        <div>
          <h2>🎯 맞춤 축제 추천</h2>
          <div className="top-recommendation">
            <h3>🏆 최우선 추천: {recommendations.top_recommendation.title}</h3>
            <p>점수: {recommendations.top_recommendation.score}점</p>
            <p>이유: {recommendations.top_recommendation.why_best}</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default FestivalRecommendation;
```

#### 5-2. Python 클라이언트 예시
```python
import requests
import json

class NamdoBotClient:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
    
    def start_conversation(self, travel_period, companion_type):
        """봇 대화 시작"""
        url = f"{self.base_url}/bot/greeting"
        data = {
            "travel_period": travel_period,
            "companion_type": companion_type
        }
        
        response = requests.post(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()
    
    def update_conversation(self, session_id, **kwargs):
        """대화 세션 업데이트"""
        url = f"{self.base_url}/bot/conversation/{session_id}"
        response = requests.put(url, headers=self.headers, json=kwargs)
        response.raise_for_status()
        return response.json()
    
    def get_final_recommendations(self, session_id):
        """최종 추천 받기"""
        url = f"{self.base_url}/bot/finalize"
        data = {"session_id": session_id}
        
        response = requests.post(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()

# 사용 예시
client = NamdoBotClient("http://localhost:8000", "your_jwt_token")

# 대화 시작
conversation = client.start_conversation("10월", "부모님 동반 가족")
print(f"세션 ID: {conversation['session_id']}")

# 에너지 레벨 선택
client.update_conversation(conversation['session_id'], energy_preference="여유로운 분위기")

# 최종 추천 받기
recommendations = client.get_final_recommendations(conversation['session_id'])
print(f"추천 축제: {recommendations['top_recommendation']['title']}")
```

### 6. 🔄 에러 처리 및 재시도

#### 6-1. 네트워크 에러 처리
```python
import time
from requests.exceptions import RequestException

def api_call_with_retry(func, max_retries=3, delay=1):
    """재시도 로직이 포함된 API 호출"""
    for attempt in range(max_retries):
        try:
            return func()
        except RequestException as e:
            if attempt == max_retries - 1:
                raise e
            print(f"API 호출 실패 (시도 {attempt + 1}/{max_retries}): {e}")
            time.sleep(delay * (2 ** attempt))  # 지수 백오프
```

#### 6-2. 토큰 만료 처리
```python
def handle_token_expiry(client, original_func, *args, **kwargs):
    """토큰 만료 시 자동 재로그인"""
    try:
        return original_func(*args, **kwargs)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            # 토큰 만료, 재로그인 시도
            new_token = client.refresh_token()
            client.headers['Authorization'] = f'Bearer {new_token}'
            return original_func(*args, **kwargs)
        raise e
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
