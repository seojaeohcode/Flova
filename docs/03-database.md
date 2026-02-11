# 데이터베이스 스키마 상세

## 전체 테이블 구조

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

---

## 테이블 관계도

```
users (사용자)
    │
    └── conversations (대화 세션) ── 1:N 관계

festivals (축제 기본 정보)
    │
    ├── festival_details (축제 상세 정보) ── 1:1 관계
    ├── festival_intros (축제 소개 정보) ── 1:1 관계
    └── pet_infos (반려동물 정보) ── 1:1 관계
```

---

## 컬럼 상세 설명

### Users 테이블
| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| id | INT | PK, AUTO_INCREMENT | 사용자 고유 ID |
| username | VARCHAR(255) | UNIQUE, NOT NULL | 사용자명 (로그인용) |
| email | VARCHAR(255) | UNIQUE, NOT NULL | 이메일 주소 |
| full_name | VARCHAR(255) | NOT NULL | 사용자 실명 |
| hashed_password | VARCHAR(255) | NOT NULL | bcrypt 암호화된 비밀번호 |
| profile_picture | VARCHAR(255) | NULL | 프로필 사진 URL |
| is_active | BOOLEAN | DEFAULT TRUE | 계정 활성 상태 |
| created_at | TIMESTAMP | DEFAULT NOW | 계정 생성 시간 |
| updated_at | TIMESTAMP | ON UPDATE | 정보 수정 시간 |

### Conversations 테이블
| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| id | INT | PK, AUTO_INCREMENT | 대화 세션 고유 ID |
| user_id | INT | FK, NOT NULL | 사용자 ID |
| session_id | VARCHAR(255) | UNIQUE, NOT NULL | 세션 식별자 (UUID) |
| travel_period | VARCHAR(50) | NULL | 여행 시기 (예: 10월, 봄) |
| companion_type | VARCHAR(100) | NULL | 동반자 유형 |
| has_pets | BOOLEAN | DEFAULT FALSE | 반려동물 동반 여부 |
| child_age_group | VARCHAR(50) | NULL | 아동 연령대 |
| energy_preference | VARCHAR(100) | NULL | 선호 분위기 |
| interest_focus | VARCHAR(100) | NULL | 핵심 관심사 |
| additional_requirements | TEXT | NULL | 추가 고려사항 |
| phase | VARCHAR(50) | DEFAULT 'initial' | 대화 단계 |
| status | VARCHAR(50) | DEFAULT 'active' | 세션 상태 |

### Festivals 테이블
| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| id | INT | PK, AUTO_INCREMENT | 축제 고유 ID |
| contentid | VARCHAR(50) | UNIQUE, NOT NULL | TourAPI 콘텐츠 ID |
| title | VARCHAR(500) | NOT NULL | 축제 제목 |
| contenttypeid | VARCHAR(50) | NULL | 콘텐츠 타입 ID |
| addr1, addr2 | VARCHAR(500) | NULL | 주소 |
| start_date, end_date | VARCHAR(20) | NULL | 축제 시작/종료일 (YYYYMMDD) |
| image | VARCHAR(1000) | NULL | 대표 이미지 URL |
| progresstype | VARCHAR(100) | NULL | 진행 유형 |
| festivaltype | VARCHAR(100) | NULL | 축제 유형 |
| tel | VARCHAR(100) | NULL | 연락처 |
| region | VARCHAR(100) | NULL | 지역 (전북, 전남, 광주) |

---

## 인덱스 전략

```sql
CREATE INDEX idx_festivals_region_date ON festivals(region, start_date, end_date);
CREATE INDEX idx_festivals_type_region ON festivals(festivaltype, region);
CREATE INDEX idx_conversations_user_status ON conversations(user_id, status);
CREATE INDEX idx_conversations_session_phase ON conversations(session_id, phase);
CREATE INDEX idx_festivals_search ON festivals(region, festivaltype, start_date);
CREATE INDEX idx_conversations_user_created ON conversations(user_id, created_at);
```

---

## 데이터 무결성 제약조건

```sql
-- 외래키 (CREATE TABLE 내 정의됨)
-- conversations.user_id → users(id) ON DELETE CASCADE
-- festival_details.contentid → festivals(contentid) ON DELETE CASCADE
-- festival_intros.contentid → festivals(contentid) ON DELETE CASCADE
-- pet_infos.contentid → festivals(contentid) ON DELETE CASCADE

-- 체크 제약조건 (MySQL 8.0+)
ALTER TABLE users ADD CONSTRAINT chk_username_length CHECK (LENGTH(username) >= 3 AND LENGTH(username) <= 20);
ALTER TABLE users ADD CONSTRAINT chk_password_length CHECK (LENGTH(hashed_password) >= 8);
ALTER TABLE conversations ADD CONSTRAINT chk_phase_values CHECK (phase IN ('initial', 'energy_preference', 'interest_focus', 'final'));
ALTER TABLE conversations ADD CONSTRAINT chk_status_values CHECK (status IN ('active', 'completed', 'expired'));
```

[← 프로젝트 구조](02-structure.md) | [메인 README](../README.md) | [다음: API 명세 →](04-api.md)
