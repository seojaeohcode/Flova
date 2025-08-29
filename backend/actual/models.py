# models.py

from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime

# ==================== 사용자 관련 모델 ====================

class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserInfo(BaseModel):
    id: int
    username: str
    full_name: Optional[str] = None

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
    status: str
    database: str