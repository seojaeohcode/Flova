#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MySQL 연결 테스트 스크립트
네이버 클라우드 MySQL 서버와의 연결을 확인합니다.
"""

import pymysql
import sys
from datetime import datetime

def test_mysql_connection():
    """MySQL 연결 테스트"""
    
    # 연결 정보
    config = {
        'host': 'db-37h1g8-kr.vpc-pub-cdb.ntruss.com',
        'port': 3306,
        'user': 'flova_user',
        'password': 'flova06*',
        'charset': 'utf8mb4',
        'autocommit': True
    }
    
    print("🔍 MySQL 연결 테스트 시작...")
    print(f"📡 호스트: {config['host']}")
    print(f"🔌 포트: {config['port']}")
    print(f"👤 사용자: {config['user']}")
    print(f"⏰ 테스트 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    try:
        # 1. 기본 연결 테스트
        print("1️⃣ 기본 연결 테스트 중...")
        connection = pymysql.connect(**config)
        print("✅ MySQL 서버 연결 성공!")
        
        # 2. 데이터베이스 목록 조회
        print("\n2️⃣ 데이터베이스 목록 조회 중...")
        with connection.cursor() as cursor:
            cursor.execute("SHOW DATABASES")
            databases = cursor.fetchall()
            print("📚 사용 가능한 데이터베이스:")
            for db in databases:
                print(f"   - {db[0]}")
        
        # 3. 데이터베이스 생성 테스트
        print("\n3️⃣ 데이터베이스 생성 테스트 중...")
        db_name = "namdo_festival"
        
        with connection.cursor() as cursor:
            # 데이터베이스가 이미 존재하는지 확인
            cursor.execute(f"SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '{db_name}'")
            exists = cursor.fetchone()
            
            if exists:
                print(f"✅ 데이터베이스 '{db_name}' 이미 존재합니다.")
            else:
                # 데이터베이스 생성
                cursor.execute(f"CREATE DATABASE `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                print(f"✅ 데이터베이스 '{db_name}' 생성 성공!")
        
        # 4. 데이터베이스 선택 및 테이블 생성 테스트
        print(f"\n4️⃣ 데이터베이스 '{db_name}' 선택 및 테이블 생성 테스트 중...")
        connection.select_db(db_name)
        
        # 테스트 테이블 생성
        test_table_sql = """
        CREATE TABLE IF NOT EXISTS `test_connection` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            `test_message` VARCHAR(255) NOT NULL,
            `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        
        with connection.cursor() as cursor:
            cursor.execute(test_table_sql)
            print("✅ 테스트 테이블 생성 성공!")
        
        # 5. 데이터 삽입/조회 테스트
        print("\n5️⃣ 데이터 삽입/조회 테스트 중...")
        
        with connection.cursor() as cursor:
            # 테스트 데이터 삽입
            insert_sql = "INSERT INTO test_connection (test_message) VALUES (%s)"
            test_message = f"연결 테스트 성공 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            cursor.execute(insert_sql, (test_message,))
            
            # 삽입된 데이터 조회
            cursor.execute("SELECT * FROM test_connection ORDER BY created_at DESC LIMIT 1")
            result = cursor.fetchone()
            
            if result:
                print(f"✅ 데이터 삽입/조회 성공!")
                print(f"   ID: {result[0]}")
                print(f"   메시지: {result[1]}")
                print(f"   생성시간: {result[2]}")
        
        # 6. 연결 정보 확인
        print("\n6️⃣ 연결 정보 확인 중...")
        
        with connection.cursor() as cursor:
            # 서버 버전 확인
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"🐬 MySQL 버전: {version[0]}")
            
            # 현재 데이터베이스 확인
            cursor.execute("SELECT DATABASE()")
            current_db = cursor.fetchone()
            print(f"📁 현재 데이터베이스: {current_db[0]}")
            
            # 사용자 권한 확인
            cursor.execute("SHOW GRANTS")
            grants = cursor.fetchall()
            print(f"🔐 사용자 권한:")
            for grant in grants[:3]:  # 처음 3개만 출력
                print(f"   - {grant[0]}")
            if len(grants) > 3:
                print(f"   ... 외 {len(grants) - 3}개 권한")
        
        # 7. 테스트 테이블 정리
        print("\n7️⃣ 테스트 테이블 정리 중...")
        
        with connection.cursor() as cursor:
            cursor.execute("DROP TABLE IF EXISTS test_connection")
            print("✅ 테스트 테이블 삭제 완료!")
        
        print("\n" + "=" * 50)
        print("🎉 모든 MySQL 연결 테스트가 성공적으로 완료되었습니다!")
        print("✅ 백엔드 애플리케이션에서 MySQL을 사용할 수 있습니다.")
        print("=" * 50)
        
        return True
        
    except pymysql.Error as e:
        print(f"\n❌ MySQL 연결 오류 발생:")
        print(f"   오류 코드: {e.args[0]}")
        print(f"   오류 메시지: {e.args[1]}")
        print(f"\n🔧 문제 해결 방법:")
        
        if e.args[0] == 2003:
            print("   - 네트워크 연결 확인")
            print("   - ACG 설정 확인")
            print("   - 호스트 주소 확인")
        elif e.args[0] == 1045:
            print("   - 사용자명/비밀번호 확인")
            print("   - 사용자 권한 확인")
        elif e.args[0] == 1049:
            print("   - 데이터베이스 존재 여부 확인")
        
        return False
        
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류 발생: {str(e)}")
        return False
        
    finally:
        if 'connection' in locals():
            connection.close()
            print("\n🔌 MySQL 연결이 종료되었습니다.")

def test_sqlalchemy_connection():
    """SQLAlchemy를 통한 MySQL 연결 테스트"""
    
    print("\n🔍 SQLAlchemy MySQL 연결 테스트 시작...")
    
    try:
        from sqlalchemy import create_engine, text
        from sqlalchemy.exc import SQLAlchemyError
        
        # SQLAlchemy 엔진 생성
        database_url = "mysql+pymysql://flova_user:flova06*@db-37h1g8-kr.vpc-pub-cdb.ntruss.com:3306/flova?charset=utf8mb4"
        
        print("🔧 SQLAlchemy 엔진 생성 중...")
        engine = create_engine(database_url, echo=False)
        
        # 연결 테스트
        print("📡 데이터베이스 연결 테스트 중...")
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            
            if row and row[0] == 1:
                print("✅ SQLAlchemy MySQL 연결 성공!")
                return True
            else:
                print("❌ SQLAlchemy 연결 테스트 실패")
                return False
                
    except ImportError:
        print("❌ SQLAlchemy가 설치되지 않았습니다.")
        print("   pip install sqlalchemy pymysql 실행 필요")
        return False
        
    except SQLAlchemyError as e:
        print(f"❌ SQLAlchemy 오류: {str(e)}")
        return False
        
    except Exception as e:
        print(f"❌ 예상치 못한 오류: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 네이버 클라우드 MySQL 연결 테스트")
    print("=" * 50)
    
    # 기본 연결 테스트
    basic_test = test_mysql_connection()
    
    if basic_test:
        # SQLAlchemy 연결 테스트
        sqlalchemy_test = test_sqlalchemy_connection()
        
        if sqlalchemy_test:
            print("\n🎯 모든 테스트가 성공했습니다!")
            print("📝 백엔드 애플리케이션을 실행할 수 있습니다.")
            sys.exit(0)
        else:
            print("\n⚠️ SQLAlchemy 테스트가 실패했습니다.")
            print("📝 의존성 설치를 확인해주세요.")
            sys.exit(1)
    else:
        print("\n❌ MySQL 연결 테스트가 실패했습니다.")
        print("📝 네트워크 설정과 사용자 정보를 확인해주세요.")
        sys.exit(1)
