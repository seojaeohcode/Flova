# database.py

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL 환경변수가 설정되지 않았습니다.")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    profile_picture = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(String(255), unique=True, index=True, nullable=False)
    phase = Column(String(50), nullable=True, default="initial")
    status = Column(String(50), nullable=True, default="active")
    travel_period = Column(String(50), nullable=True)
    companion_type = Column(String(100), nullable=True)
    has_pets = Column(Boolean, default=False, nullable=True)
    child_age_group = Column(String(50), nullable=True)
    energy_preference = Column(String(100), nullable=True)
    interest_focus = Column(String(100), nullable=True)
    additional_requirements = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Festival(Base):
    __tablename__ = "festivals"

    id = Column(Integer, primary_key=True, index=True)
    contentid = Column(String(50), unique=True, index=True, nullable=False)
    title = Column(String(500), nullable=False)
    contenttypeid = Column(String(50), nullable=True)
    addr1 = Column(String(500), nullable=True)
    start_date = Column(String(20), nullable=True)
    end_date = Column(String(20), nullable=True)
    image = Column(String(1000), nullable=True)
    progresstype = Column(String(100), nullable=True)
    festivaltype = Column(String(100), nullable=True)
    tel = Column(String(100), nullable=True)
    region = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class FestivalDetail(Base):
    __tablename__ = "festival_details"

    id = Column(Integer, primary_key=True, index=True)
    contentid = Column(String(50), ForeignKey("festivals.contentid"), nullable=False)
    title = Column(String(500), nullable=False)
    createdtime = Column(String(20), nullable=True)
    modifiedtime = Column(String(20), nullable=True)
    tel = Column(String(100), nullable=True)
    telname = Column(String(100), nullable=True)
    homepage = Column(String(1000), nullable=True)
    firstimage = Column(String(1000), nullable=True)
    firstimage2 = Column(String(1000), nullable=True)
    addr1 = Column(String(500), nullable=True)
    addr2 = Column(String(500), nullable=True)
    mapx = Column(String(50), nullable=True)
    mapy = Column(String(50), nullable=True)
    mlevel = Column(String(50), nullable=True)
    overview = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class FestivalIntro(Base):
    __tablename__ = "festival_intros"

    id = Column(Integer, primary_key=True, index=True)
    contentid = Column(String(50), ForeignKey("festivals.contentid"), nullable=False)
    sponsor1 = Column(String(200), nullable=True)
    sponsor1tel = Column(String(100), nullable=True)
    sponsor2 = Column(String(200), nullable=True)
    eventenddate = Column(String(20), nullable=True)
    playtime = Column(String(200), nullable=True)
    eventplace = Column(String(500), nullable=True)
    eventstartdate = Column(String(20), nullable=True)
    usetimefestival = Column(String(500), nullable=True)
    progresstype = Column(String(100), nullable=True)
    festivaltype = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class PetInfo(Base):
    __tablename__ = "pet_infos"

    id = Column(Integer, primary_key=True, index=True)
    contentid = Column(String(50), ForeignKey("festivals.contentid"), nullable=False)
    acmpyPsblCpam = Column(String(200), nullable=True)
    relaRntlPrdlst = Column(String(500), nullable=True)
    acmpyNeedMtr = Column(String(500), nullable=True)
    etcAcmpyInfo = Column(Text, nullable=True)
    relaPurcPrdlst = Column(String(500), nullable=True)
    relaAcdntRiskMtr = Column(String(500), nullable=True)
    acmpyTypeCd = Column(String(50), nullable=True)
    relaPosesFclty = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    Base.metadata.create_all(bind=engine)
