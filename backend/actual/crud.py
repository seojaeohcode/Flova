# crud.py

from sqlalchemy.orm import Session
import uuid
from typing import Optional, List

# 로컬 모듈 임포트
from database import User, Conversation, ConversationMessage, UserPreference
from models import ConversationInit, UserPreferenceCreate

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

def add_conversation_message(db: Session, conversation_id: int, role: str, content: str, turn_number: int):
    db_message = ConversationMessage(
        conversation_id=conversation_id, role=role, content=content, turn_number=turn_number
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def get_conversation_messages(db: Session, conversation_id: int):
    return db.query(ConversationMessage).filter(
        ConversationMessage.conversation_id == conversation_id
    ).order_by(ConversationMessage.turn_number).all()

# ==================== 사용자 선호도 CRUD (추가) ====================

def get_preferences_by_user_id(db: Session, user_id: int) -> List[UserPreference]:
    """사용자 ID로 모든 선호도 정보 조회"""
    return db.query(UserPreference).filter(UserPreference.user_id == user_id).all()

def update_user_preference(db: Session, user_id: int, pref_data: UserPreferenceCreate):
    """사용자 선호도 생성 또는 업데이트"""
    db_pref = db.query(UserPreference).filter(
        UserPreference.user_id == user_id,
        UserPreference.preference_type == pref_data.preference_type
    ).first()

    if db_pref:
        db_pref.preference_value = pref_data.preference_value
    else:
        db_pref = UserPreference(
            user_id=user_id,
            preference_type=pref_data.preference_type,
            preference_value=pref_data.preference_value
        )
        db.add(db_pref)
    
    db.commit()
    db.refresh(db_pref)
    return db_pref