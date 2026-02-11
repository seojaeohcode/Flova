# 문제 해결·성능·향후 계획

## 문제 해결

### 자주 나오는 이슈
1. **Import 에러**: `schemas.models`, `core.database` 등 필요한 모듈이 모두 정의되어 있는지 확인
2. **DB 연결 실패**: `.env`의 `DATABASE_URL` 값·네트워크 확인
3. **API 키**: `TOUR_API_KEY`, `CLOVASTUDIO_API_KEY` 설정 여부 확인

### 로그 확인 (배포 환경)
```bash
sudo journalctl -u namdo-bot -f
sudo journalctl -u namdo-bot --no-pager -n 100
```

---

## 성능 최적화

- **DB**: 자주 조회하는 컬럼에 인덱스 (예: `region`, `start_date`, `user_id`, `session_id`)
- **LLM**: 동일 질문에 대한 응답 캐싱 검토
- **비동기**: FastAPI 비동기 라우트·DB 호출 활용

---

## 향후 계획

- [ ] FAISS 기반 의미 검색 강화
- [ ] 추천 품질 개선을 위한 사용자 피드백 수집
- [ ] React Native 등 모바일 앱
- [ ] 새 축제 정보 실시간 알림

[← API 사용 예시](09-api-examples.md) | [메인 README](../README.md) | [다음: 라이선스·기여 →](11-license.md)
