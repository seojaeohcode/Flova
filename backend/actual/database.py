# database.py

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.sql import func
import os
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=3600)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """데이터베이스 세션 생성"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==================== 데이터베이스 모델 ====================

class User(Base):
    """사용자 정보"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    profile_picture = Column(String(255), nullable=True)  # 프로필 사진 URL 저장
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    conversations = relationship("Conversation", back_populates="user")
    # [추가] UserPreference와의 관계 설정
    preferences = relationship("UserPreference", back_populates="user")

class Conversation(Base):
    """대화 세션"""
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # --- 사전 입력 정보 저장을 위한 컬럼 ---
    travel_period = Column(String(20))
    companion_type = Column(String(50))
    has_pets = Column(Boolean, default=False)
    child_age_group = Column(String(50), nullable=True)

    # --- 대화 진행 중 쌓이는 정보 ---
    phase = Column(String(20), default="initial")
    energy_preference = Column(String(20))
    interest_focus = Column(String(50))
    additional_requirements = Column(Text)
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    user = relationship("User", back_populates="conversations")
    messages = relationship("ConversationMessage", back_populates="conversation")

class ConversationMessage(Base):
    """대화 메시지"""
    __tablename__ = "conversation_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    turn_number = Column(Integer, default=1)
    created_at = Column(DateTime, default=func.now())
    
    conversation = relationship("Conversation", back_populates="messages")

# [추가] 사용자 선호도 저장을 위한 테이블 모델
class UserPreference(Base):
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    preference_type = Column(String(50), index=True)  # 예: "default_companion", "default_has_pets"
    preference_value = Column(String(100))          # 예: "아이 동반 가족", "true"
    
    user = relationship("User", back_populates="preferences")


def create_tables():
    """테이블 생성"""
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    print("🚀 데이터베이스 테이블 생성 중...")
    create_tables()
    print("✅ 테이블 생성 완료!")