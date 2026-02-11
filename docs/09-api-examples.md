# API 사용 예시

## 1. 인증 플로우 (curl)

### 회원가입
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username":"traveler123","email":"traveler@example.com","full_name":"김여행","password":"securepassword123"}'
```

### 로그인
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"traveler123","password":"securepassword123"}'
```
→ 응답의 `access_token`을 저장 후 `Authorization: Bearer {token}` 으로 사용

---

## 2. 봇 대화 (curl)

### 봇 인사 및 첫 질문
```bash
curl -X POST "http://localhost:8000/bot/greeting" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"travel_period":"10월","companion_type":"부모님 동반 가족"}'
```

### 최종 추천
```bash
curl -X POST "http://localhost:8000/bot/finalize" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"session_id":"550e8400-e29b-41d4-a716-446655440000"}'
```

---

## 3. 축제 검색·추천 (curl)

### 검색
```bash
curl -X GET "http://localhost:8000/festivals/search?region=전북&festival_type=음식축제&page=1&limit=10" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### 직접 추천
```bash
curl -X POST "http://localhost:8000/festivals/recommend" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"travel_period":"10월","companion_type":"부모님 동반 가족","atmosphere":"여유로운 분위기","core_experience":"음식","additional_considerations":"걷기 최소화"}'
```

---

## 4. 헬스 체크
```bash
curl -X GET "http://localhost:8000/health"
```

---

## 5. Python 클라이언트 예시

```python
import requests

class NamdoBotClient:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    def start_conversation(self, travel_period, companion_type):
        r = requests.post(f"{self.base_url}/bot/greeting", headers=self.headers,
                          json={"travel_period": travel_period, "companion_type": companion_type})
        r.raise_for_status()
        return r.json()

    def get_final_recommendations(self, session_id):
        r = requests.post(f"{self.base_url}/bot/finalize", headers=self.headers, json={"session_id": session_id})
        r.raise_for_status()
        return r.json()

# 사용
client = NamdoBotClient("http://localhost:8000", "your_jwt_token")
conv = client.start_conversation("10월", "부모님 동반 가족")
rec = client.get_final_recommendations(conv["session_id"])
```

---

더 많은 예시(React 컴포넌트, 에러·재시도 처리)는 이전 통합 README를 참고하거나 서버 `/docs` 에서 확인할 수 있습니다.

[← 기술 스택](08-tech-stack.md) | [메인 README](../README.md) | [다음: 문제 해결·성능·향후 계획 →](10-operations.md)
