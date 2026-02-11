# crud.py

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import uuid
from typing import Optional, List

# 로컬 모듈 임포트
from database import User, Conversation, Festival, FestivalDetail, FestivalIntro, PetInfo
from models import UserCreate, UserInfo, ConversationInit
from auth import get_password_hash

# ==================== 사용자 CRUD ====================

def create_user(db: Session, username: str, email: str, hashed_password: str, full_name: str = None, profile_picture: str = None) -> User:
    db_user = User(username=username, email=email, hashed_password=hashed_password, full_name=full_name, profile_picture=profile_picture)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()

def update_user_profile(db: Session, user_id: int, full_name: str = None, profile_picture: str = None) -> Optional[User]:
    """사용자 프로필 정보 업데이트"""
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        if full_name is not None:
            user.full_name = full_name
        if profile_picture is not None:
            user.profile_picture = profile_picture
        db.commit()
        db.refresh(user)
    return user

# ==================== 대화 세션 CRUD ====================

def create_conversation(db: Session, user_id: int, init_data: ConversationInit) -> Conversation:
    session_id = str(uuid.uuid4())
    db_conversation = Conversation(
        session_id=session_id,
        user_id=user_id,
        phase="initial",
        status="active",
        travel_period=init_data.travel_period,
        companion_type=init_data.companion_type,
        has_pets=init_data.has_pets,
        child_age_group=init_data.child_age_group
    )
    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)
    return db_conversation

def get_conversation_by_session_id(db: Session, session_id: str):
    return db.query(Conversation).filter(Conversation.session_id == session_id).first()

def update_conversation_phase(db: Session, conversation_id: int, phase: str, **kwargs):
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if conversation:
        conversation.phase = phase
        for key, value in kwargs.items():
            if hasattr(conversation, key):
                setattr(conversation, key, value)
        db.commit()
        db.refresh(conversation)
    return conversation

# ConversationMessage 관련 함수는 제거됨 (새로운 RAG 시스템에서는 불필요)

# 사용자 선호도 관련 함수는 제거됨 (새로운 RAG 시스템에서는 불필요)

# 축제 관련 CRUD 함수들
def create_festival(db: Session, festival_data: dict) -> Festival:
    """축제 기본 정보 생성"""
    db_festival = Festival(**festival_data)
    db.add(db_festival)
    db.commit()
    db.refresh(db_festival)
    return db_festival

def get_festival_by_contentid(db: Session, contentid: str) -> Optional[Festival]:
    """contentid로 축제 조회"""
    return db.query(Festival).filter(Festival.contentid == contentid).first()

def get_festivals_by_region(db: Session, region: str) -> List[Festival]:
    """지역별 축제 목록 조회"""
    return db.query(Festival).filter(Festival.region == region).all()

def get_festivals_by_period(db: Session, start_date: str, end_date: str) -> List[Festival]:
    """기간별 축제 목록 조회"""
    return db.query(Festival).filter(
        and_(
            Festival.start_date >= start_date,
            Festival.end_date <= end_date
        )
    ).all()

def create_festival_detail(db: Session, detail_data: dict) -> FestivalDetail:
    """축제 상세 정보 생성"""
    db_detail = FestivalDetail(**detail_data)
    db.add(db_detail)
    db.commit()
    db.refresh(db_detail)
    return db_detail

def create_festival_intro(db: Session, intro_data: dict) -> FestivalIntro:
    """축제 소개 정보 생성"""
    db_intro = FestivalIntro(**intro_data)
    db.add(db_intro)
    db.commit()
    db.refresh(db_intro)
    return db_intro

def create_pet_info(db: Session, pet_data: dict) -> PetInfo:
    """반려동물 정보 생성"""
    db_pet_info = PetInfo(**pet_data)
    db.add(db_pet_info)
    db.commit()
    db.refresh(db_pet_info)
    return db_pet_info

def get_festival_with_details(db: Session, contentid: str) -> Optional[dict]:
    """축제의 모든 정보를 함께 조회"""
    festival = get_festival_by_contentid(db, contentid)
    if not festival:
        return None
    
    detail = db.query(FestivalDetail).filter(FestivalDetail.contentid == contentid).first()
    intro = db.query(FestivalIntro).filter(FestivalIntro.contentid == contentid).first()
    pet_info = db.query(PetInfo).filter(PetInfo.contentid == contentid).first()
    
    return {
        "festival": festival,
        "detail": detail,
        "intro": intro,
        "pet_info": pet_info
    }

def search_festivals(db: Session, 
                    region: Optional[str] = None,
                    period: Optional[str] = None,
                    festival_type: Optional[str] = None,
                    has_pet_info: bool = False) -> List[Festival]:
    """축제 검색 (필터링 적용)"""
    query = db.query(Festival)
    
    if region:
        query = query.filter(Festival.region == region)
    
    if period:
        query = query.filter(Festival.start_date >= period)
    
    if festival_type:
        query = query.filter(Festival.festivaltype == festival_type)
    
    if has_pet_info:
        # 반려동물 정보가 있는 축제만 필터링
        pet_contentids = db.query(PetInfo.contentid).distinct()
        query = query.filter(Festival.contentid.in_(pet_contentids))
    
    return query.all()

def create_conversation(db: Session, user_id: int, session_data: dict) -> Conversation:
    """대화 세션 생성"""
    session_id = str(uuid.uuid4())
    db_conversation = Conversation(
        user_id=user_id,
        session_id=session_id,
        **session_data
    )
    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)
    return db_conversation

def update_conversation(db: Session, session_id: str, update_data: dict) -> Optional[Conversation]:
    """대화 세션 업데이트"""
    conversation = db.query(Conversation).filter(Conversation.session_id == session_id).first()
    if not conversation:
        return None
    
    for key, value in update_data.items():
        if hasattr(conversation, key):
            setattr(conversation, key, value)
    
    db.commit()
    db.refresh(conversation)
    return conversation

def get_conversation(db: Session, session_id: str) -> Optional[Conversation]:
    """세션 ID로 대화 조회"""
    return db.query(Conversation).filter(Conversation.session_id == session_id).first()

def get_user_conversations(db: Session, user_id: int) -> List[Conversation]:
    """사용자의 모든 대화 세션 조회"""
    return db.query(Conversation).filter(Conversation.user_id == user_id).all()