# 환경 변수 설정

`backend/actual` 또는 프로젝트 루트에 `.env` 파일을 두고 아래 변수를 설정합니다.  
예시는 `backend/actual/env_example.txt`를 참고하세요.

---

## 필수 변수

| 변수 | 설명 | 예시 |
|------|------|------|
| DATABASE_URL | MySQL 연결 문자열 | `mysql+pymysql://user:pass@host:3306/flova?charset=utf8mb4` |
| TOUR_API_KEY | 공공데이터포털 TourAPI 키 | (발급 후 입력) |
| CLOVASTUDIO_API_KEY | 네이버 Clova Studio API 키 | (발급 후 입력) |
| SECRET_KEY | JWT 시크릿 (32자 이상 권장) | `openssl rand -base64 32` |

---

## 주요 선택 변수

| 변수 | 기본값 | 설명 |
|------|--------|------|
| ALGORITHM | HS256 | JWT 알고리즘 |
| ACCESS_TOKEN_EXPIRE_MINUTES | 30 | 토큰 만료(분) |
| ENVIRONMENT | production | development / production / testing |
| DEBUG | false | 디버그 모드 |
| LOG_LEVEL | INFO | DEBUG, INFO, WARNING, ERROR, CRITICAL |
| HOST | 0.0.0.0 | 서버 바인드 주소 |
| PORT | 8000 | 서버 포트 |
| MIN_PASSWORD_LENGTH | 8 | 비밀번호 최소 길이 |
| MIN_USERNAME_LENGTH | 3, MAX 20 | 사용자명 길이 |

---

## API 키 발급

### TourAPI (공공데이터포털)
1. [data.go.kr](https://www.data.go.kr/) 회원가입·로그인  
2. "TourAPI", "한국관광공사_국문 관광정보 서비스" 검색 후 신청  
3. 승인 후 키를 `TOUR_API_KEY`에 입력  

### Clova Studio (네이버)
1. [ncloud.com](https://www.ncloud.com/) 회원가입·로그인  
2. AI·NAVER API → Clova Studio → Clova X 신청  
3. 승인 후 키를 `CLOVASTUDIO_API_KEY`에 입력  

---

## 보안

```bash
# JWT 시크릿 생성
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
openssl rand -base64 32

# .env 권한 (Linux/Mac)
chmod 600 .env
```

---

## 환경별 예시

- **개발**: `ENVIRONMENT=development`, `DEBUG=true`, `LOG_LEVEL=DEBUG`, 로컬 `DATABASE_URL`  
- **테스트**: `ENVIRONMENT=testing`, 테스트 DB URL  
- **운영**: `ENVIRONMENT=production`, `DEBUG=false`, VPC DB URL  

[← 배포 방법](05-deployment.md) | [메인 README](../README.md) | [다음: 주요 기능 →](07-features.md)
