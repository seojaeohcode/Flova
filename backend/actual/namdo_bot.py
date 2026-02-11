# namdo_bot.py (전체 코드)

import logging
import json
import uuid
import os
from datetime import timedelta, datetime
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm, HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from pydantic import BaseModel

# --- 로컬 모듈 임포트 ---
from core.database import get_db, create_tables, Conversation, User
from core.auth import authenticate_user, create_access_token, get_current_active_user, create_user_helper, ACCESS_TOKEN_EXPIRE_MINUTES
from crud import (
    create_conversation, get_conversation_by_session_id, update_conversation_phase,
    update_user_profile
)
from schemas.models import (
    UserCreate, Token, UserInfo, ConversationInit, ConversationUpdate,
    ChatResponse, RecommendationResponse, HealthCheck, FestivalRecommendation,
    UserPreference, UserPreferenceCreate, FestivalRecommendationRequest, FestivalRecommendationResponse,
    BotGreetingRequest, BotGreetingResponse, XAIFinalizeRequest, XAIFinalizeResponse,
    StructuredRecommendationResponse, TopRecommendation, AlternativeRecommendation, ScoreBreakdown, RecommendationCriteria
)
from services.tour_api import get_festivals_by_name
from langchain_naver import ChatClovaX
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from services.festival_service import festival_service
from langchain.output_parsers import PydanticOutputParser

# --- 로깅 및 FastAPI 앱 설정 ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()

app = FastAPI(
    title="남도봇 축제 추천 시스템",
    description="AI 기반 멀티턴 대화형 남도 축제 추천 시스템",
    version="1.0.0"
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# ==================== RAG/LLM 연동 ====================

# LangChain RAG 시스템 초기화
def initialize_rag_system():
    """LangChain RAG 시스템 초기화"""
    try:
        # ClovaX LLM 초기화
        llm = ChatClovaX(
            model="clova-x-1-5-20240607",
            api_key=os.getenv("CLOVASTUDIO_API_KEY"),
            temperature=0.1  # 일관된 출력을 위해 낮은 temperature
        )
        
        # PydanticOutputParser 초기화
        parser = PydanticOutputParser(pydantic_object=StructuredRecommendationResponse)
        
        # RAG 프롬프트 템플릿
        rag_prompt_template = PromptTemplate(
            input_variables=["context", "user_preferences", "festival_data"],
            template="""
            당신은 호남 지역 축제 추천 전문가입니다.
            
            사용자 정보:
            {user_preferences}
            
            축제 데이터:
            {festival_data}
            
            컨텍스트:
            {context}
            
            반드시 아래 JSON 형식으로만 대답하세요:
            {format_instructions}
            
            중요: 자연어가 아닌 JSON 형식으로만 응답하세요.
            """,
            partial_variables={"format_instructions": parser.get_format_instructions()}
        )
        
        # RAG 체인 생성
        rag_chain = LLMChain(llm=llm, prompt=rag_prompt_template)
        
        return rag_chain, parser
        
    except Exception as e:
        print(f"RAG 시스템 초기화 실패: {e}")
        return None, None

# RAG 시스템 초기화
rag_chain, response_parser = initialize_rag_system()

async def generate_llm_recommendations(conversation: Conversation) -> List[FestivalRecommendation]:
    # TODO: 향후 대화 시나리오에 지역을 묻는 단계를 추가하고, DB에서 해당 값을 가져오도록 수정해야 합니다.
    # 현재는 예시로 '전라북도 부안군'을 하드코딩합니다.
    region_name = "전라북도"
    sigungu_name = "부안군"
    
    current_year = datetime.now().year
    month = int(conversation.travel_period.replace("월", ""))
    event_start_date = f"{current_year}{month:02d}01"

    festivals = get_festivals_by_name(region_name, sigungu_name, event_start_date)
    
    if festivals is None:
        raise HTTPException(status_code=503, detail="외부 축제 정보를 가져오는 데 실패했습니다. 잠시 후 다시 시도해주세요.")
    if not festivals:
        return []

    context_str = "\n".join([f"- 축제명: {f['title']}, 주소: {f['addr1']}, 기간: {f['start_date']}~{f['end_date']}" for f in festivals])
    user_preferences_str = (
        f"- 여행 시기: {conversation.travel_period}\n"
        f"- 동반자: {conversation.companion_type}\n"
        f"- 반려동물 동반: {'예' if conversation.has_pets else '아니오'}\n"
        f"- 자녀 나이대: {conversation.child_age_group or '해당 없음'}\n"
        f"- 선호 분위기: {conversation.energy_preference}\n"
        f"- 핵심 관심사: {conversation.interest_focus}\n"
        f"- 추가 요청사항: {conversation.additional_requirements}"
    )
    
    result_json_str = rag_chain.run(context=context_str, user_preferences=user_preferences_str, festival_data=context_str)
    
    try:
        # PydanticOutputParser를 사용하여 구조화된 응답을 파싱합니다.
        structured_recommendations = response_parser.parse(result_json_str)
        
        # 파싱된 데이터를 FestivalRecommendation 모델로 변환합니다.
        recommendations = [FestivalRecommendation(**rec.dict()) for rec in structured_recommendations.recommendations]
        
        for rec in recommendations:
            for fest in festivals:
                if fest['title'] == rec.name:
                    rec.image_url = fest['image']
                    break
        return recommendations
        
    except Exception as e:
        logger.error(f"LLM 응답 파싱 실패: {e}")
        logger.error(f"원본 LLM 응답: {result_json_str}")
        raise HTTPException(status_code=500, detail="추천 결과를 생성하는 데 실패했습니다.")

# ==================== 대화 시나리오 정의 ====================
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
        "options": None,
        "next_phase": "additional_requirements"
    },
    "additional_requirements": {
        "message": "알겠습니다! 모든 정보를 바탕으로 사용자님께 꼭 맞는 축제를 추천해 드릴게요! 잠시만 기다려주세요.",
        "options": None,
        "next_phase": "completed"
    }
}

# ==================== API 엔드포인트 ====================



@app.post("/register", response_model=UserInfo, tags=["Authentication"])
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    try:
        user = create_user_helper(db=db, **user_data.model_dump())
        return UserInfo(id=user.id, username=user.username, full_name=user.full_name, profile_picture=user.profile_picture)
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
    return UserInfo(id=current_user.id, username=current_user.username, full_name=current_user.full_name, profile_picture=current_user.profile_picture)

@app.put("/users/me/profile", response_model=UserInfo, tags=["Authentication"])
async def update_user_profile(
    full_name: str = None,
    profile_picture: str = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """사용자 프로필 정보 업데이트"""
    updated_user = update_user_profile(db, current_user.id, full_name, profile_picture)
    if not updated_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="사용자를 찾을 수 없습니다")
    return UserInfo(
        id=updated_user.id, 
        username=updated_user.username, 
        full_name=updated_user.full_name,
        profile_picture=updated_user.profile_picture
    )

@app.get("/users/me/preferences", response_model=List[UserPreference], tags=["User Preferences"])
async def read_user_preferences(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return get_preferences_by_user_id(db, user_id=current_user.id)

@app.post("/users/me/preferences", response_model=UserPreference, tags=["User Preferences"])
async def write_user_preference(pref_data: UserPreferenceCreate, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return update_user_preference(db, user_id=current_user.id, pref_data=pref_data)

@app.post("/initialize", response_model=ChatResponse, tags=["Festival Recommendation"])
async def initialize_conversation(init_data: ConversationInit, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    conversation = create_conversation(db, current_user.id, init_data)
    scenario = CONVERSATION_SCENARIO["initial"]
    message = scenario["message"].format(travel_period=init_data.travel_period, companion_type=init_data.companion_type)
    add_conversation_message(db, conversation.id, "assistant", message, 1)
    return ChatResponse(session_id=conversation.session_id, message=message, turn_number=1, phase="initial", options=scenario["options"], is_final=False)

@app.post("/chat", response_model=ChatResponse, tags=["Festival Recommendation"])
async def chat(chat_data: ConversationUpdate, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    conversation = get_conversation_by_session_id(db, chat_data.session_id)
    if not conversation or conversation.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="유효하지 않은 세션 ID입니다.")
    current_turn = len(get_conversation_messages(db, conversation.id)) + 1
    add_conversation_message(db, conversation.id, "user", chat_data.user_response, current_turn)
    current_phase = conversation.phase
    scenario_step = CONVERSATION_SCENARIO.get(current_phase)
    if not scenario_step:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="잘못된 대화 단계입니다.")
    update_data = {}
    if current_phase == "initial":
        update_data["energy_preference"] = "활기찬" if "A" in chat_data.selected_option else "여유로운"
    elif current_phase == "energy_preference":
        update_data["interest_focus"] = "자연" if "A" in chat_data.selected_option else "음식" if "B" in chat_data.selected_option else "역사"
    elif current_phase == "interest_focus":
        update_data["additional_requirements"] = chat_data.user_response
    next_phase = scenario_step["next_phase"]
    update_conversation_phase(db, conversation.id, next_phase, **update_data)
    next_scenario_step = CONVERSATION_SCENARIO[next_phase]
    message = next_scenario_step["message"].format(companion_type=conversation.companion_type)
    is_final = next_phase == "additional_requirements"
    if is_final:
        update_conversation_phase(db, conversation.id, "completed", status="completed")
    add_conversation_message(db, conversation.id, "assistant", message, current_turn + 1)
    return ChatResponse(session_id=chat_data.session_id, message=message, turn_number=current_turn + 1, phase=next_phase, options=next_scenario_step["options"], is_final=is_final)

@app.get("/recommendations/{session_id}", response_model=RecommendationResponse, tags=["Festival Recommendation"])
async def get_recommendations(session_id: str, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    conversation = get_conversation_by_session_id(db, session_id)
    if not conversation or conversation.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="유효하지 않은 세션 ID입니다.")
    if conversation.phase != "completed":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="추천을 생성하기 위한 대화가 완료되지 않았습니다.")
    recommendations = await generate_llm_recommendations(conversation)
    conversation_summary = f"{conversation.travel_period} {conversation.companion_type}와(과) 함께 떠나는 {conversation.energy_preference} {conversation.interest_focus} 여행"
    return RecommendationResponse(recommendations=recommendations, conversation_summary=conversation_summary, total_turns=len(get_conversation_messages(db, conversation.id)))

# ==================== 헬스체크 및 상태 확인 API ====================

@app.get("/health", response_model=HealthCheck, tags=["Health Check"])
async def health_check():
    """
    시스템 상태를 확인하는 헬스체크 엔드포인트
    """
    return HealthCheck(
        status="healthy",
        message="남도봇 축제 추천 시스템이 정상 작동 중입니다",
        timestamp=datetime.now().isoformat(),
        version="1.0.0"
    )

@app.get("/", tags=["Root"])
async def root():
    """
    루트 경로 - 시스템 정보 제공
    """
    return {
        "message": "남도봇 축제 추천 시스템에 오신 것을 환영합니다!",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# ==================== [추가] 단순 축제 검색 테스트용 API ====================

class FestivalSearchRequest(BaseModel):
    region_name: str
    sigungu_name: Optional[str] = None
    event_start_date: str # "YYYYMMDD" 형식

@app.post("/api/festivals/search", tags=["Development & Test"])
async def search_festivals_directly(req: FestivalSearchRequest):
    """
    TourAPI 연동 테스트를 위해 지역명과 날짜로 축제 목록을 직접 조회합니다.
    (로그인 필요 없음)
    """
    logger.info(f"단순 검색 요청: {req.region_name} {req.sigungu_name or ''}, 시작일: {req.event_start_date}")
    
    festivals = get_festivals_by_name(
        region_name=req.region_name,
        sigungu_name=req.sigungu_name,
        event_start_date=req.event_start_date
    )

    if festivals is None:
        raise HTTPException(status_code=503, detail="TourAPI 호출에 실패했습니다. .env 파일의 TOUR_API_KEY 또는 네트워크를 확인하세요.")
    
    if not festivals:
        return {"message": "해당 조건에 맞는 축제가 없습니다.", "festivals": []}
        
    return {"message": f"총 {len(festivals)}개의 축제를 찾았습니다.", "festivals": festivals}

# 축제 관련 API 엔드포인트들
@app.post("/festivals/collect", response_model=dict)
async def collect_festival_data(
    db: Session = Depends(get_db),
    current_user: UserInfo = Depends(get_current_active_user)
):
    """호남 지역 축제 데이터 수집 (관리자용)"""
    try:
        total_collected = festival_service.collect_all_honam_festivals(db)
        return {
            "message": "축제 데이터 수집 완료",
            "total_collected": total_collected,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"축제 데이터 수집 실패: {str(e)}"
        )

@app.get("/festivals/search")
async def search_festivals(
    region: Optional[str] = None,
    period: Optional[str] = None,
    festival_type: Optional[str] = None,
    has_pet_info: bool = False,
    db: Session = Depends(get_db),
    current_user: UserInfo = Depends(get_current_active_user)
):
    """축제 검색"""
    try:
        festivals = festival_service.search_festivals(
            db, region, period, festival_type, has_pet_info
        )
        return {
            "festivals": festivals,
            "total_count": len(festivals),
            "filters": {
                "region": region,
                "period": period,
                "festival_type": festival_type,
                "has_pet_info": has_pet_info
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"축제 검색 실패: {str(e)}"
        )

@app.post("/festivals/recommend", response_model=FestivalRecommendationResponse)
async def recommend_festivals(
    request: FestivalRecommendationRequest,
    db: Session = Depends(get_db),
    current_user: UserInfo = Depends(get_current_active_user)
):
    """사용자 조건에 맞는 축제 추천"""
    try:
        recommendations = festival_service.get_festival_recommendations(
            db,
            request.travel_period,
            request.companion_type,
            request.atmosphere,
            request.core_experience,
            request.additional_considerations
        )
        
        # 응답 형식 변환
        festival_recommendations = []
        for rec in recommendations:
            festival_recommendations.append({
                "title": rec["festival"].title,
                "contentid": rec["festival"].contentid,
                "region": rec["festival"].region,
                "start_date": rec["festival"].start_date,
                "end_date": rec["festival"].end_date,
                "location": rec["festival"].addr1,
                "description": f"점수: {rec['score']}, 이유: {', '.join(rec['reasons'])}",
                "why_recommended": ", ".join(rec["reasons"]),
                "pet_friendly": bool(rec["festival"].contentid),  # 간단한 체크
                "accessibility_info": "상세 정보는 축제 상세 조회를 통해 확인 가능합니다."
            })
        
        return FestivalRecommendationResponse(
            recommendations=festival_recommendations,
            total_count=len(festival_recommendations),
            reasoning=f"사용자 조건: {request.travel_period} {request.companion_type} {request.atmosphere} {request.core_experience} {request.additional_considerations}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"축제 추천 실패: {str(e)}"
        )

# 봇 시작말 API
@app.post("/bot/greeting", response_model=BotGreetingResponse)
async def bot_greeting(
    request: BotGreetingRequest,
    db: Session = Depends(get_db),
    current_user: UserInfo = Depends(get_current_active_user)
):
    """봇의 시작말 및 첫 번째 질문 제공"""
    try:
        # 대화 세션 생성
        session_data = {
            "travel_period": request.travel_period,
            "companion_type": request.companion_type
        }
        conversation = create_conversation(db, current_user.id, session_data)
        
        # 계절별 특징 매핑
        season_features = {
            "3월": "봄꽃이 피어나고 따뜻한 봄바람이 부는",
            "4월": "벚꽃이 만발하고 새싹이 돋아나는",
            "5월": "푸른 잎이 무성하고 산들바람이 부는",
            "6월": "초록이 짙어지고 여름의 문턱에 선",
            "7월": "푸른 여름이 한창이고 맑은 하늘이 펼쳐진",
            "8월": "한여름의 열기가 가득하고 푸른 자연이 아름다운",
            "9월": "가을의 문턱에 서서 선선한 바람이 부는",
            "10월": "가을 단풍이 절정에 달하고 하늘이 높아진",
            "11월": "단풍이 물들고 서늘한 가을 정취가 가득한",
            "12월": "겨울의 문턱에 서서 차가운 바람이 부는"
        }
        
        # 동반자별 특징 매핑
        companion_features = {
            "혼자": "자유롭고 독립적인",
            "연인": "로맨틱하고 특별한",
            "친구": "즐겁고 활기찬",
            "아이 동반 가족": "아이들과 함께하는 즐거운",
            "부모님 동반 가족": "부모님과 함께하는 의미있는"
        }
        
        season_feature = season_features.get(request.travel_period, "아름다운")
        companion_feature = companion_features.get(request.companion_type, "특별한")
        
        # 시작말 생성
        greeting_message = f"""안녕하세요! {request.travel_period}에 {request.companion_type}와(과) 함께하는 호남 여행을 계획하고 계시는군요! 😊

{season_feature} 시기 저희 호남은 {companion_feature} 여행을 위한 최고의 장소랍니다. 

소중한 분과 함께하는 여행을 계획하는 그 마음, 저도 잘 알기에 진심으로 응원하게 되네요. 

수많은 축제 정보 속에서 길을 잃지 않도록, 제가 여러분의 스타일에 꼭 맞는 '인생 축제'를 찾아 평생 기억에 남을 추억을 설계해 드릴게요.

가장 완벽한 추천을 위해, 먼저 여러분이 꿈꾸시는 여행의 전반적인 분위기를 함께 그려보고 싶어요. 어떤 그림에 더 마음이 끌리시나요?"""

        # 첫 번째 질문과 선택지
        next_question = "여행의 전체적인 분위기를 선택해주세요:"
        choices = [
            "활기찬 체험형 여행 - 다양한 볼거리와 흥미진진한 프로그램들",
            "여유로운 감상형 여행 - 아름다운 풍경을 배경으로 한 고즈넉한 축제"
        ]
        
        return BotGreetingResponse(
            greeting_message=greeting_message,
            next_question=next_question,
            choices=choices,
            session_id=conversation.session_id
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"봇 시작말 생성 실패: {str(e)}"
        )

@app.get("/bot/conversation/{session_id}")
async def get_conversation_status(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: UserInfo = Depends(get_current_active_user)
):
    """대화 세션 상태 조회"""
    conversation = get_conversation_by_session_id(db, session_id) # Changed from get_conversation to get_conversation_by_session_id
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="대화 세션을 찾을 수 없습니다."
        )
    
    if conversation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="해당 대화 세션에 접근할 권한이 없습니다."
        )
    
    return {
        "session_id": conversation.session_id,
        "travel_period": conversation.travel_period,
        "companion_type": conversation.companion_type,
        "atmosphere": conversation.energy_preference, # Changed from conversation.atmosphere to conversation.energy_preference
        "core_experience": conversation.interest_focus, # Changed from conversation.core_experience to conversation.interest_focus
        "additional_considerations": conversation.additional_requirements, # Changed from conversation.additional_requirements to conversation.additional_requirements
        "created_at": conversation.created_at,
        "updated_at": conversation.updated_at
    }

@app.put("/bot/conversation/{session_id}")
async def update_conversation_status(
    session_id: str,
    update_data: dict,
    db: Session = Depends(get_db),
    current_user: UserInfo = Depends(get_current_active_user)
):
    """대화 세션 상태 업데이트"""
    conversation = get_conversation_by_session_id(db, session_id) # Changed from get_conversation to get_conversation_by_session_id
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="대화 세션을 찾을 수 없습니다."
        )
    
    if conversation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="해당 대화 세션에 접근할 권한이 없습니다."
        )
    
    updated_conversation = update_conversation(db, session_id, update_data)
    if not updated_conversation:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="대화 세션 업데이트 실패"
        )
    
    return {
        "message": "대화 세션이 업데이트되었습니다.",
        "session_id": updated_conversation.session_id,
        "updated_at": updated_conversation.updated_at
    }

# XAI 마무리 API
@app.post("/bot/finalize", response_model=XAIFinalizeResponse)
async def finalize_conversation_with_xai(
    request: XAIFinalizeRequest,
    db: Session = Depends(get_db),
    current_user: UserInfo = Depends(get_current_active_user)
):
    """대화 세션을 마무리하고 XAI 기반 최종 추천 및 설명 제공"""
    try:
        # 대화 세션 조회
        conversation = get_conversation_by_session_id(db, request.session_id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="대화 세션을 찾을 수 없습니다."
            )
        
        if conversation.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="해당 대화 세션에 접근할 권한이 없습니다."
            )
        
        # 축제 추천 실행
        recommendations = festival_service.get_festival_recommendations(
            db,
            conversation.travel_period,
            conversation.companion_type,
            conversation.energy_preference or "기본",
            conversation.interest_focus or "기본",
            conversation.additional_requirements or "기본"
        )
        
        if not recommendations:
            # 추천이 없는 경우 기본 응답
            return XAIFinalizeResponse(
                session_id=request.session_id,
                user_profile={
                    "travel_period": conversation.travel_period,
                    "companion_type": conversation.companion_type,
                    "energy_preference": conversation.energy_preference or "미정",
                    "interest_focus": conversation.interest_focus or "미정",
                    "additional_requirements": conversation.additional_requirements or "없음"
                },
                recommendation_summary={
                    "total_count": 0,
                    "message": "추천할 축제를 찾을 수 없습니다."
                },
                top_recommendation=TopRecommendation(
                    title="",
                    region="",
                    start_date="",
                    end_date="",
                    location="",
                    score=0,
                    reasons=[],
                    why_best=""
                ),
                alternative_recommendations=[],
                score_breakdown=ScoreBreakdown(
                    region_compatibility=0,
                    season_matching=0,
                    companion_optimization=0,
                    interest_matching=0,
                    accessibility_consideration=0,
                    total_score=0
                ),
                recommendation_criteria=RecommendationCriteria(
                    region_priority="호남 지역",
                    season_focus=conversation.travel_period,
                    companion_type=conversation.companion_type,
                    interest_focus=conversation.interest_focus or "기본",
                    accessibility_focus=conversation.additional_requirements or "기본"
                ),
                reasoning_summary={
                    "message": "더 구체적인 정보를 제공해주시면 정확한 추천이 가능합니다.",
                    "suggestions": ["여행 분위기를 선택해주세요", "핵심 관심사를 선택해주세요", "추가 고려사항을 입력해주세요"]
                },
                timestamp=datetime.now().isoformat()
            )
        
        # LangChain RAG를 사용하여 구조화된 응답 생성
        if rag_chain and response_parser:
            try:
                # 축제 데이터를 문자열로 변환
                festival_data_str = "\n".join([
                    f"제목: {rec['festival'].title}, 지역: {rec['festival'].region}, "
                    f"기간: {rec['festival'].start_date}~{rec['festival'].end_date}, "
                    f"위치: {rec['festival'].addr1}, 점수: {rec['score']}, "
                    f"이유: {', '.join(rec['reasons'])}"
                    for rec in recommendations
                ])
                
                # 사용자 선호도 정보
                user_preferences_str = f"""
                여행 시기: {conversation.travel_period}
                동반자: {conversation.companion_type}
                선호 분위기: {conversation.energy_preference or '기본'}
                핵심 관심사: {conversation.interest_focus or '기본'}
                추가 고려사항: {conversation.additional_requirements or '없음'}
                """
                
                # 컨텍스트 정보
                context_str = f"호남 지역 축제 추천 시스템 - {len(recommendations)}개 축제 중 최적의 선택"
                
                # LangChain RAG 실행
                llm_response = rag_chain.run(
                    context=context_str,
                    user_preferences=user_preferences_str,
                    festival_data=festival_data_str
                )
                
                # PydanticOutputParser로 파싱
                structured_response = response_parser.parse(llm_response)
                
                # 파싱된 응답을 XAIFinalizeResponse로 변환
                return XAIFinalizeResponse(
                    session_id=request.session_id,
                    user_profile={
                        "travel_period": conversation.travel_period,
                        "companion_type": conversation.companion_type,
                        "energy_preference": conversation.energy_preference or "기본",
                        "interest_focus": conversation.interest_focus or "기본",
                        "additional_requirements": conversation.additional_requirements or "없음"
                    },
                    recommendation_summary={
                        "total_count": len(recommendations),
                        "message": structured_response.user_profile_summary,
                        "score_range": {
                            "highest": max(rec["score"] for rec in recommendations),
                            "lowest": min(rec["score"] for rec in recommendations)
                        }
                    },
                    top_recommendation=TopRecommendation(
                        title=structured_response.top_recommendation.title,
                        region=structured_response.top_recommendation.region,
                        start_date=structured_response.top_recommendation.start_date,
                        end_date=structured_response.top_recommendation.end_date,
                        location=structured_response.top_recommendation.location,
                        score=structured_response.top_recommendation.score,
                        reasons=structured_response.top_recommendation.reasons,
                        why_best=structured_response.top_recommendation.why_recommended,
                        image=structured_response.top_recommendation.image,
                        tel=structured_response.top_recommendation.tel
                    ),
                    alternative_recommendations=[
                        AlternativeRecommendation(
                            rank=i+2,
                            title=alt.title,
                            region=alt.region,
                            start_date=alt.start_date,
                            end_date=alt.end_date,
                            location=alt.location,
                            score=alt.score,
                            reasons=alt.reasons,
                            why_alternative=alt.why_recommended,
                            image=alt.image,
                            tel=alt.tel
                        )
                        for i, alt in enumerate(structured_response.alternative_recommendations)
                    ],
                    score_breakdown=ScoreBreakdown(
                        region_compatibility=structured_response.score_breakdown.get("region_compatibility", 0),
                        season_matching=structured_response.score_breakdown.get("season_matching", 0),
                        companion_optimization=structured_response.score_breakdown.get("companion_optimization", 0),
                        interest_matching=structured_response.score_breakdown.get("interest_matching", 0),
                        accessibility_consideration=structured_response.score_breakdown.get("accessibility_consideration", 0),
                        total_score=structured_response.score_breakdown.get("total_score", 0)
                    ),
                    recommendation_criteria=RecommendationCriteria(
                        region_priority="호남 지역 (전북, 전남, 광주)",
                        season_focus=conversation.travel_period,
                        companion_type=conversation.companion_type,
                        interest_focus=conversation.interest_focus or "기본",
                        accessibility_focus=conversation.additional_requirements or "기본"
                    ),
                    reasoning_summary={
                        "message": structured_response.reasoning_explanation,
                        "suggestions": [
                            "추천된 축제의 상세 정보를 확인해보세요",
                            "2순위 이하 축제도 고려해보세요",
                            "추가 질문이 있으면 언제든 물어보세요"
                        ]
                    },
                    timestamp=datetime.now().isoformat()
                )
                
            except Exception as e:
                logger.error(f"LangChain RAG 처리 실패: {e}")
                # RAG 실패 시 기존 로직으로 fallback
                pass
        
        # 기존 로직 (fallback)
        # 추천이 없는 경우 기본 응답
        return XAIFinalizeResponse(
            session_id=request.session_id,
            user_profile={
                "travel_period": conversation.travel_period,
                "companion_type": conversation.companion_type,
                "energy_preference": conversation.energy_preference or "미정",
                "interest_focus": conversation.interest_focus or "미정",
                "additional_requirements": conversation.additional_requirements or "없음"
            },
            recommendation_summary={
                "total_count": 0,
                "message": "추천할 축제를 찾을 수 없습니다."
            },
            top_recommendation=TopRecommendation(
                title="",
                region="",
                start_date="",
                end_date="",
                location="",
                score=0,
                reasons=[],
                why_best=""
            ),
            alternative_recommendations=[],
            score_breakdown=ScoreBreakdown(
                region_compatibility=0,
                season_matching=0,
                companion_optimization=0,
                interest_matching=0,
                accessibility_consideration=0,
                total_score=0
            ),
            recommendation_criteria=RecommendationCriteria(
                region_priority="호남 지역",
                season_focus=conversation.travel_period,
                companion_type=conversation.companion_type,
                interest_focus=conversation.interest_focus or "기본",
                accessibility_focus=conversation.additional_requirements or "기본"
            ),
            reasoning_summary={
                "message": "더 구체적인 정보를 제공해주시면 정확한 추천이 가능합니다.",
                "suggestions": ["여행 분위기를 선택해주세요", "핵심 관심사를 선택해주세요", "추가 고려사항을 입력해주세요"]
            },
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"XAI 마무리 처리 실패: {str(e)}"
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