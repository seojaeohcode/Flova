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
from auth import authenticate_user, create_access_token, get_current_active_user, create_user_helper, ACCESS_TOKEN_EXPIRE_MINUTES
from crud import (
    create_conversation, get_conversation_by_session_id, update_conversation_phase,
    add_conversation_message, get_conversation_messages,
    get_preferences_by_user_id, update_user_preference
)
from models import (
    UserCreate, Token, UserInfo, ConversationInit, ConversationUpdate,
    ChatResponse, RecommendationResponse, HealthCheck, FestivalRecommendation,
    UserPreference, UserPreferenceCreate
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

# ==================== RAG/LLM 연동 (시연용) ====================
fake_response = {
    "recommendations": [
        {"rank": 1, "name": "순창장류축제", "location": "전북 순창", "description": "건강한 발효 음식의 향연", "image_url": "https://via.placeholder.com/300x200.png?text=Sunchang+Festival", "reason": "요청하신 '음식'과 '여유로운' 분위기에 가장 잘 맞고, '걷기 편한' 장점을 갖춰 부모님께 안성맞춤입니다.", "xai_explanation": "TOP 1 선정 이유: 부모님과의 '여유로운 음식 여행'이라는 핵심 요구사항을 100% 만족하며, 편의성까지 고려된 최적의 선택지입니다."},
        {"rank": 2, "name": "남원흥부제", "location": "전북 남원", "description": "맛과 멋이 어우러진 전통 축제", "image_url": "https://via.placeholder.com/300x200.png?text=Namwon+Festival", "reason": "맛있는 '남원추어탕'을 편하게 즐길 수 있고, 전통문화를 체험할 수 있어 '마음이 즐거운' 여행이 됩니다.", "xai_explanation": "TOP 2 선정 이유: '음식'과 '문화'를 동시에 만족시키며, 앉아서 즐길 수 있는 프로그램이 많아 편안한 여행이 가능합니다."},
    ]
}
fake_llm = FakeListLLM(responses=[json.dumps(fake_response, ensure_ascii=False)])

rag_prompt_template = PromptTemplate(
    input_variables=["context", "user_preferences"], 
    template="사용자 요청: {user_preferences}\n\n추천 결과:" # 간단한 예시 프롬프트
)
rag_chain = LLMChain(llm=fake_llm, prompt=rag_prompt_template)

async def generate_llm_recommendations(conversation: Conversation) -> List[FestivalRecommendation]:
    """ [완성] 대화 내용을 바탕으로 LLM/RAG를 호출하여 추천 결과를 생성하는 함수 """
    user_preferences = (
        f"- 여행 시기: {conversation.travel_period}\n"
        f"- 동반자: {conversation.companion_type}\n"
        f"- 반려동물 동반: {'예' if conversation.has_pets else '아니오'}\n"
        f"- 자녀 나이대: {conversation.child_age_group or '해당 없음'}\n"
        f"- 선호 분위기: {conversation.energy_preference}\n"
        f"- 핵심 관심사: {conversation.interest_focus}\n"
        f"- 추가 요청사항: {conversation.additional_requirements}"
    )
    
    # 실제 RAG Chain은 context에 검색 결과를 자동으로 채워줍니다.
    result_json_str = rag_chain.run(context="[RAG에 의해 검색된 축제 정보들]", user_preferences=user_preferences)
    
    try:
        result_data = json.loads(result_json_str)
        return [FestivalRecommendation(**rec) for rec in result_data.get("recommendations", [])]
    except (json.JSONDecodeError, TypeError) as e:
        logger.error(f"LLM 응답 파싱 실패: {e}")
        raise HTTPException(status_code=500, detail="추천 결과를 생성하는 데 실패했습니다.")

# [완성] 대화 시나리오 대본
CONVERSATION_SCENARIO = {
    "initial": {
        "message": "안녕하세요! {travel_period}에 {companion_type}와(과) 함께 떠나는 멋진 호남 여행을 계획하고 계시는군요! 😊\n\n이번 여행의 전체적인 분위기는 어떤 느낌을 선호하시나요?",
        "options": ["A: 다양한 볼거리와 체험이 가득한 활기찬 분위기", "B: 아름다운 풍경을 보며 즐기는 여유롭고 고즈넉한 분위기"],
        "next_phase": "energy_preference"
    },
    "energy_preference": {
        "message": "좋은 선택이에요! ✨\n\n그렇다면 이번 여행에서 가장 만족하셨으면 하는 '핵심 경험'은 무엇일까요?",
        "options": ["A: 눈이 즐거운 것 (아름다운 가을 꽃이나 단풍 구경)", "B: 입이 즐거운 것 (제철 식재료로 만든 건강한 남도 음식)", "C: 마음이 즐거운 것 (역사 유적지나 고즈넉한 사찰 탐방)"],
        "next_phase": "interest_focus"
    },
    "interest_focus": {
        "message": "역시 맛의 고장 호남 여행의 핵심은 음식이군요! 👍\n\n마지막으로 하나만 더 여쭤볼게요. 혹시 꼭 고려해야 할 점이 있을까요?\n\n예를 들어, '오래 걷는 것은 괜찮으신지' 혹은 '편하게 앉아서 쉴 공간이 많은 곳'이 좋은지 알려주시면, 정말 딱 맞는 곳으로 찾아 드릴게요!",
        "options": None, # 주관식 답변을 받으므로 선택지는 없음
        "next_phase": "additional_requirements"
    },
    "additional_requirements": {
        "message": "알겠습니다! 모든 정보를 바탕으로 사용자님께 꼭 맞는 축제를 추천해 드릴게요! 잠시만 기다려주세요.",
        "options": None,
        "next_phase": "completed"
    }
}

# ==================== API 엔드포인트 ====================

@app.get("/", tags=["Root"])
async def root(): return {"message": "남도봇 축제 추천 시스템", "docs": "/docs"}

@app.get("/health", response_model=HealthCheck, tags=["Health"])
async def health_check(db: Session = Depends(get_db)):
    try:
        db.execute("SELECT 1")
        db_status = "connected"
    except Exception:
        db_status = "disconnected"
    return HealthCheck(status="healthy", database=db_status)

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
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return Token(access_token=access_token, token_type="bearer", expires_in=int(access_token_expires.total_seconds()))

@app.get("/users/me", response_model=UserInfo, tags=["Authentication"])
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return UserInfo(id=current_user.id, username=current_user.username, full_name=current_user.full_name)

# ==================== 사용자 선호도 관리 API ====================

@app.get("/users/me/preferences", response_model=List[UserPreference], tags=["User Preferences"])
async def read_user_preferences(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return get_preferences_by_user_id(db, user_id=current_user.id)

@app.post("/users/me/preferences", response_model=UserPreference, tags=["User Preferences"])
async def write_user_preference(pref_data: UserPreferenceCreate, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return update_user_preference(db, user_id=current_user.id, pref_data=pref_data)

# ==================== 축제 추천 관련 엔드포인트 ====================

@app.post("/initialize", response_model=ChatResponse, tags=["Festival Recommendation"])
async def initialize_conversation(init_data: ConversationInit, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    conversation = create_conversation(db, current_user.id, init_data)
    scenario = CONVERSATION_SCENARIO["initial"]
    message = scenario["message"].format(travel_period=init_data.travel_period, companion_type=init_data.companion_type)
    add_conversation_message(db, conversation.id, "assistant", message, 1)
    return ChatResponse(session_id=conversation.session_id, message=message, turn_number=1, phase="initial", options=scenario["options"], is_final=False)

@app.post("/chat", response_model=ChatResponse, tags=["Festival Recommendation"])
async def chat(chat_data: ConversationUpdate, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """ [완성] 대화 진행 및 다음 질문 또는 최종 요약 메시지 반환 함수 """
    conversation = get_conversation_by_session_id(db, chat_data.session_id)
    if not conversation or conversation.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="유효하지 않은 세션 ID입니다.")

    current_turn = len(get_conversation_messages(db, conversation.id)) + 1
    add_conversation_message(db, conversation.id, "user", chat_data.user_response, current_turn)

    current_phase = conversation.phase
    scenario_step = CONVERSATION_SCENARIO.get(current_phase)
    if not scenario_step:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="잘못된 대화 단계입니다.")

    # --- 대화 내용 DB에 저장 ---
    update_data = {}
    if current_phase == "initial":
        update_data["energy_preference"] = "활기찬" if "A" in chat_data.selected_option else "여유로운"
    elif current_phase == "energy_preference":
        update_data["interest_focus"] = "자연" if "A" in chat_data.selected_option else "음식" if "B" in chat_data.selected_option else "역사"
    elif current_phase == "interest_focus":
        update_data["additional_requirements"] = chat_data.user_response
    
    # --- 다음 단계로 상태 전이 ---
    next_phase = scenario_step["next_phase"]
    update_conversation_phase(db, conversation.id, next_phase, **update_data)
    
    # --- 다음 AI 응답 생성 ---
    next_scenario_step = CONVERSATION_SCENARIO[next_phase]
    message = next_scenario_step["message"].format(companion_type=conversation.companion_type) # 간단한 format
    
    is_final = next_phase == "additional_requirements"
    if is_final:
        update_conversation_phase(db, conversation.id, "completed", status="completed")

    add_conversation_message(db, conversation.id, "assistant", message, current_turn + 1)
    
    return ChatResponse(
        session_id=chat_data.session_id,
        message=message,
        turn_number=current_turn + 1,
        phase=next_phase,
        options=next_scenario_step["options"],
        is_final=is_final
    )

@app.get("/recommendations/{session_id}", response_model=RecommendationResponse, tags=["Festival Recommendation"])
async def get_recommendations(session_id: str, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    conversation = get_conversation_by_session_id(db, session_id)
    if not conversation or conversation.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="유효하지 않은 세션 ID입니다.")
    if conversation.phase != "completed":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="추천을 생성하기 위한 대화가 완료되지 않았습니다.")

    recommendations = await generate_llm_recommendations(conversation)
    conversation_summary = f"{conversation.travel_period} {conversation.companion_type}와(과) 함께 떠나는 {conversation.energy_preference} {conversation.interest_focus} 여행"
    return RecommendationResponse(
        recommendations=recommendations,
        conversation_summary=conversation_summary,
        total_turns=len(get_conversation_messages(db, conversation.id))
    )

# ==================== 애플리케이션 시작 이벤트 ====================
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 남도봇 축제 추천 시스템 시작 중...")
    try:
        create_tables()
        logger.info("✅ 데이터베이스 테이블 생성 완료")
        logger.info("🎉 시스템 시작 완료! API 문서: http://127.0.0.1:8000/docs")
    except Exception as e:
        logger.error(f"❌ 시스템 시작 실패: {e}")

# ==================== 메인 실행 ====================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("namdo_bot:app", host="0.0.0.0", port=8000, reload=True)