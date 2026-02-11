# check_db.py
from sqlalchemy import create_engine, inspect
import os
from dotenv import load_dotenv

# .env 파일에서 데이터베이스 URL 불러오기
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("오류: .env 파일에서 DATABASE_URL을 찾을 수 없습니다.")
else:
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as connection:
            print("✅ 데이터베이스 연결 성공!")
            inspector = inspect(engine)
            table_names = inspector.get_table_names()

            if table_names:
                print("\n📜 생성된 테이블 목록:")
                for name in table_names:
                    print(f"- {name}")
            else:
                print("\n⚠️ 생성된 테이블이 없습니다.")

    except Exception as e:
        print(f"❌ 데이터베이스 연결 또는 조회 중 오류 발생: {e}")