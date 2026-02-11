# schemas/models.py (Pydantic API models)

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

# ==================== 사용자 관련 모델 ====================

class UserBase(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None
    profile_picture: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserInfo(BaseModel):
    id: int
    username: str
    full_name: Optional[str] = None
    profile_picture: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

# ==================== 대화 관련 모델 ====================

class ConversationInit(BaseModel):
    travel_period: str
    companion_type: str
    has_pets: bool = False
    child_age_group: Optional[str] = None

class ConversationUpdate(BaseModel):
    session_id: str
    user_response: str
    selected_option: Optional[str] = None

class FestivalRecommendation(BaseModel):
    rank: int
    name: str
    location: str
    description: str
    image_url: str
    reason: str
    xai_explanation: str

class ChatResponse(BaseModel):
    session_id: str
    message: str
    turn_number: int
    phase: str
    options: Optional[List[str]] = None
    is_final: bool = False

class RecommendationResponse(BaseModel):
    recommendations: List[FestivalRecommendation]
    conversation_summary: str
    total_turns: int

# ==================== 사용자 선호도 모델 (추가) ====================

class UserPreferenceBase(BaseModel):
    preference_type: str
    preference_value: str

class UserPreferenceCreate(UserPreferenceBase):
    pass

class UserPreference(UserPreferenceBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

# ==================== 시스템 상태 모델 ====================

class HealthCheck(BaseModel):
    message: str
    timestamp: str
    version: str

# 축제 관련 모델 추가
class FestivalBase(BaseModel):
    title: str
    contentid: str
    contenttypeid: str
    addr1: str
    start_date: str
    end_date: str
    image: str
    progresstype: str
    festivaltype: str
    tel: str
    region: str

class FestivalDetail(BaseModel):
    contentid: str
    title: str
    createdtime: str
    modifiedtime: str
    tel: str
    telname: str
    homepage: str
    firstimage: str
    firstimage2: str
    addr1: str
    addr2: str
    mapx: str
    mapy: str
    mlevel: str
    overview: str

class FestivalIntro(BaseModel):
    contentid: str
    sponsor1: str
    sponsor1tel: str
    sponsor2: str
    eventenddate: str
    playtime: str
    eventplace: str
    eventstartdate: str
    usetimefestival: str
    progresstype: str
    festivaltype: str

class PetInfo(BaseModel):
    contentid: str
    acmpyPsblCpam: str
    relaRntlPrdlst: str
    acmpyNeedMtr: str
    etcAcmpyInfo: str
    relaPurcPrdlst: str
    relaAcdntRiskMtr: str
    acmpyTypeCd: str
    relaPosesFclty: str

# 축제 추천 요청 모델
class FestivalRecommendationRequest(BaseModel):
    travel_period: str
    companion_type: str
    atmosphere: str
    core_experience: str
    additional_considerations: str

# 축제 추천 응답 모델
class FestivalRecommendation(BaseModel):
    title: str
    contentid: str
    region: str
    start_date: str
    end_date: str
    location: str
    description: str
    why_recommended: str
    pet_friendly: bool
    accessibility_info: str

class FestivalRecommendationResponse(BaseModel):
    recommendations: List[FestivalRecommendation]
    total_count: int
    reasoning: str

# 봇 시작말 요청/응답 모델
class BotGreetingRequest(BaseModel):
    travel_period: str
    companion_type: str

class BotGreetingResponse(BaseModel):
    greeting_message: str
    next_question: str
    choices: List[str]
    session_id: str

# XAI 마무리 요청/응답 모델
class XAIFinalizeRequest(BaseModel):
    session_id: str

class XAIFinalizeResponse(BaseModel):
    session_id: str
    user_profile_summary: str
    recommendation_summary: str
    top_recommendation: dict
    alternative_recommendations: List[dict]
    reasoning_explanation: str
    final_message: str
    timestamp: str

# LangChain PydanticOutputParser용 모델들
class FestivalRecommendationItem(BaseModel):
    title: str
    region: str
    start_date: str
    end_date: str
    location: str
    score: int
    reasons: List[str]
    why_recommended: str
    image: Optional[str] = None
    tel: Optional[str] = None

class TopRecommendation(BaseModel):
    title: str
    region: str
    start_date: str
    end_date: str
    location: str
    score: int
    reasons: List[str]
    why_best: str
    image: Optional[str] = None
    tel: Optional[str] = None

class AlternativeRecommendation(BaseModel):
    rank: int
    title: str
    region: str
    start_date: str
    end_date: str
    location: str
    score: int
    reasons: List[str]
    why_alternative: str
    image: Optional[str] = None
    tel: Optional[str] = None

class ScoreBreakdown(BaseModel):
    region_compatibility: int
    season_matching: int
    companion_optimization: int
    interest_matching: int
    accessibility_consideration: int
    total_score: int

class RecommendationCriteria(BaseModel):
    region_priority: str
    season_focus: str
    companion_type: str
    interest_focus: str
    accessibility_focus: str

class StructuredRecommendationResponse(BaseModel):
    user_profile_summary: str
    top_recommendation: FestivalRecommendationItem
    alternative_recommendations: List[FestivalRecommendationItem]
    score_breakdown: dict
    reasoning_explanation: str
    final_message: str
