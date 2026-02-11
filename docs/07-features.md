# 주요 기능 상세

## 1. AI 기반 축제 추천

- **LangChain RAG**: FAISS 벡터 검색, 사용자 선호도·축제 정보 결합, 동적 프롬프트
- **ClovaX LLM**: 한국어 특화, 자연스러운 대화·추천
- **구조화 응답**: PydanticOutputParser, 스키마 검증, 파싱 실패 시 fallback

## 2. 멀티턴 대화

- **Phase 1**: 여행 시기, 동반자 유형
- **Phase 2**: 분위기 선호 (활기찬 vs 여유로운)
- **Phase 3**: 핵심 관심사 (자연/음식/문화)
- **Phase 4**: 추가 요구사항 (접근성, 편의시설 등)
- **세션**: UUID 기반 추적, 상태 저장, 복구·만료 처리
- **프로필**: 대화 기반 선호도 분석, 맥락 유지, 개인화 추천

## 3. XAI (설명 가능 AI)

- **score_breakdown**: region_compatibility, season_matching, companion_optimization, interest_matching, accessibility_consideration, total_score
- **점수 요소**: 지역 가중치, 계절 매칭, 동반자·관심사·접근성 반영
- **대안 추천**: 1순위 최적, 2–3순위 우수, 4–5순위 보완 옵션

## 4. 실시간 축제 정보

- **TourAPI**: 공공데이터포털 한국관광공사 API, 실시간 수집
- **수집**: 스케줄/증분 업데이트, 재시도·로깅, 검증
- **지역**: 전북(14 시군), 전남(22 시군), 광주(5구)

## 5. 보안·인증

- **JWT**: Stateless, 토큰 만료·갱신, bcrypt 비밀번호
- **권한**: 일반(검색·추천·대화), 관리자(수집·관리)

## 6. 데이터·인사이트

- **사용자**: 추천/대화 패턴, API 사용량
- **축제**: 계절별·지역별·유형별 트렌드

[← 환경 변수](06-environment.md) | [메인 README](../README.md) | [다음: 기술 스택 →](08-tech-stack.md)
