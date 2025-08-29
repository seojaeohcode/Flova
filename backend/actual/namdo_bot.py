# namdo_bot.py

import logging
import json
import uuid
from datetime import timedelta
from typing import List

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

# --- 로컬 모듈 임포트 ---
from database import get_db, create_tables, Conversation, User
from auth import authenticate_user, create_access_token, get_current_active_user, create_user_helper
from crud import (
    create_conversation, get_conversation_by_session_id, update_conversation_phase,
    add_conversation_message, get_conversation_messages,
    get_preferences_by_user_id, update_user_preference # [추가] 선호도 crud 함수
)
from models import (
    UserCreate, Token, UserInfo, ConversationInit, ConversationUpdate,
    ChatResponse, RecommendationResponse, HealthCheck, FestivalRecommendation,
    UserPreference, UserPreferenceCreate # [추가] 선호도 Pydantic 모델
)

# --- LLM/RAG 관련 임포트 (테스트용) ---
from langchain_community.llms import FakeListLLM
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

# --- 로깅 및 FastAPI 앱 설정 ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="남도봇 축제 추천 시스템",
    description="AI 기반 멀티턴 대화형 남도 축제 추천 시스템",
    version="1.0.0"
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# (이하 RAG/LLM 연동 및 대화 시나리오 정의 부분은 이전과 동일하므로 생략)
# ==================== RAG/LLM 연동 (시연용) ====================
fake_response = {
    "recommendations": [
        {"rank": 1, "name": "순창장류축제", "location": "전북 순창", "description": "건강한 발효 음식의 향연", "image_url": "https://via.placeholder.com/300x200.png?text=Sunchang+Festival", "reason": "요청하신 '음식'과 '여유로운' 분위기에 가장 잘 맞고, '걷기 편한' 장점을 갖춰 부모님께 안성맞춤입니다.", "xai_explanation": "TOP 1 선정 이유: 부모님과의 '여유로운 음식 여행'이라는 핵심 요구사항을 100% 만족하며, 편의성까지 고려된 최적의 선택지입니다."},
        {"rank": 2, "name": "남원흥부제", "location": "전북 남원", "description": "맛과 멋이 어우러진 전통 축제", "image_url": "https://via.placeholder.com/300x200.png?text=Namwon+Festival", "reason": "맛있는 '남원추어탕'을 편하게 즐길 수 있고, 전통문화를 체험할 수 있어 '마음이 즐거운' 여행이 됩니다.", "xai_explanation": "TOP 2 선정 이유: '음식'과 '문화'를 동시에 만족시키며, 앉아서 즐길 수 있는 프로그램이 많아 편안한 여행이 가능합니다."},
    ]
}
fake_llm = FakeListLLM(responses=[json.dumps(fake_response, ensure_ascii=False)])
rag_prompt_template = PromptTemplate(input_variables=["context", "user_preferences"], template="...") # 프롬프트 생략
rag_chain = LLMChain(llm=fake_llm, prompt=rag_prompt_template)

async def generate_llm_recommendations(conversation: Conversation) -> List[FestivalRecommendation]:
    # (함수 내용 생략)
    user_preferences = f"- 여행 시기: {conversation.travel_period}..."
    result_json_str = rag_chain.run(context="[RAG 정보]", user_preferences=user_preferences)
    result_data = json.loads(result_json_str)
    return [FestivalRecommendation(**rec) for rec in result_data.get("recommendations", [])]

CONVERSATION_SCENARIO = { "initial": {...}, "energy_preference": {...}, "interest_focus": {...}, "additional_requirements": {...} } # 시나리오 생략

# ==================== API 엔드포인트 ====================

@app.get("/", tags=["Root"])
async def root(): return {"message": "남도봇 축제 추천 시스템", "docs": "/docs"}

@app.get("/health", response_model=HealthCheck, tags=["Health"])
async def health_check(db: Session = Depends(get_db)):
    # (함수 내용 생략)
    db.execute("SELECT 1")
    return HealthCheck(status="healthy", database="connected")

@app.post("/register", response_model=UserInfo, tags=["Authentication"])
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    try:
        user = create_user_helper(db=db, **user_data.model_dump())
        return UserInfo(id=user.id, username=user.username, full_name=user.full_name)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@app.post("/token", response_model=Token, tags=["Authentication"])
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return Token(access_token=access_token, token_type="bearer", expires_in=int(access_token_expires.total_seconds()))

@app.get("/users/me", response_model=UserInfo, tags=["Authentication"])
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return UserInfo(id=current_user.id, username=current_user.username, full_name=current_user.full_name)

# ==================== 사용자 선호도 관리 API (추가) ====================

@app.get("/users/me/preferences", response_model=List[UserPreference], tags=["User Preferences"])
async def read_user_preferences(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """현재 로그인된 사용자의 저장된 선호도 정보 조회"""
    return get_preferences_by_user_id(db, user_id=current_user.id)

@app.post("/users/me/preferences", response_model=UserPreference, tags=["User Preferences"])
async def write_user_preference(pref_data: UserPreferenceCreate, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """현재 로그인된 사용자의 선호도 정보 저장/업데이트"""
    return update_user_preference(db, user_id=current_user.id, pref_data=pref_data)

# ==================== 축제 추천 관련 엔드포인트 ====================

@app.post("/initialize", response_model=ChatResponse, tags=["Festival Recommendation"])
async def initialize_conversation(init_data: ConversationInit, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    # (함수 내용 생략)
    conversation = create_conversation(db, current_user.id, init_data)
    scenario = CONVERSATION_SCENARIO["initial"]
    message = scenario["message"].format(travel_period=init_data.travel_period, companion_type=init_data.companion_type)
    add_conversation_message(db, conversation.id, "assistant", message, 1)
    return ChatResponse(session_id=conversation.session_id, message=message, turn_number=1, phase="initial", options=scenario["options"], is_final=False)

@app.post("/chat", response_model=ChatResponse, tags=["Festival Recommendation"])
async def chat(chat_data: ConversationUpdate, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    # (함수 내용 생략)
    conversation = get_conversation_by_session_id(db, chat_data.session_id)
    # ... (대화 상태 전이 로직)
    return ChatResponse(...)

@app.get("/recommendations/{session_id}", response_model=RecommendationResponse, tags=["Festival Recommendation"])
async def get_recommendations(session_id: str, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    # (함수 내용 생략)
    conversation = get_conversation_by_session_id(db, session_id)
    # ... (권한 및 완료 여부 체크)
    recommendations = await generate_llm_recommendations(conversation)
    conversation_summary = f"{conversation.travel_period} 여행"
    return RecommendationResponse(recommendations=recommendations, conversation_summary=conversation_summary, total_turns=len(get_conversation_messages(db, conversation.id)))

# ==================== 애플리케이션 시작 이벤트 ====================
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 남도봇 축제 추천 시스템 시작 중...")
    try:
        create_tables()
        logger.info("✅ 데이터베이스 테이블 생성 완료")
        logger.info("🎉 시스템 시작 완료!")
    except Exception as e:
        logger.error(f"❌ 시스템 시작 실패: {e}")

# ==================== 메인 실행 ====================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("namdo_bot:app", host="0.0.0.0", port=8000, reload=True)