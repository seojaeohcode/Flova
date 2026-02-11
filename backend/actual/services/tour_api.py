# tour_api.py

import requests
import os
import json
from dotenv import load_dotenv
from typing import List, Dict, Optional, Tuple
import ssl
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager

load_dotenv()
TOUR_API_KEY = os.getenv("TOUR_API_KEY")

KOR_SERVICE_URL = "https://apis.data.go.kr/B551011/KorService2"
FESTIVAL_API_URL = f"{KOR_SERVICE_URL}/searchFestival2"
AREA_CODE_API_URL = f"{KOR_SERVICE_URL}/areaCode2"
_area_code_cache = {}

class TlsAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False):
        ctx = ssl.create_default_context()
        ctx.set_ciphers('DEFAULT@SECLEVEL=1')
        self.poolmanager = PoolManager(
            num_pools=connections,
            maxsize=maxsize,
            block=block,
            ssl_context=ctx
        )

def _fetch_codes(session: requests.Session, area_code: str = "") -> Optional[List[Dict]]:
    params = {
        "serviceKey": TOUR_API_KEY,
        "numOfRows": 500,
        "pageNo": 1,
        "MobileOS": "ETC",
        "MobileApp": "NamdoBot",
        "_type": "json",
    }
    if area_code:
        params["areaCode"] = area_code

    try:
        print(f"  [디버그] areaCode API 호출 시작... (areaCode: {area_code or '전체'})")
        response = session.get(AREA_CODE_API_URL, params=params, timeout=5)
        response.raise_for_status()
        items = response.json().get("response", {}).get("body", {}).get("items", {}).get("item", [])
        print(f"  [디버그] areaCode API 호출 성공. {len(items)}개 결과 수신.")
        return items
    except requests.RequestException as e:
        print(f"  [디버그] ❌ areaCode API 호출 실패: {e}")
        return None

def _fetch_and_find_codes(session: requests.Session, region_name: str, sigungu_name: Optional[str] = None) -> Optional[Tuple[str, str]]:
    if "main_areas" not in _area_code_cache:
        main_areas = _fetch_codes(session)
        if main_areas is None: return None
        _area_code_cache["main_areas"] = {item['name']: item['code'] for item in main_areas}

    area_code = _area_code_cache["main_areas"].get(region_name)
    if not area_code:
        print(f"오류: '{region_name}' 광역 지역을 찾을 수 없습니다.")
        return None

    sigungu_code = ""
    if sigungu_name:
        cache_key = f"sigungu_{area_code}"
        if cache_key not in _area_code_cache:
            sigungu_areas = _fetch_codes(session, area_code=area_code)
            if sigungu_areas is None: return None
            _area_code_cache[cache_key] = {item['name']: item['code'] for item in sigungu_areas}

        sigungu_code = _area_code_cache[cache_key].get(sigungu_name)
        if sigungu_code is None:
            print(f"오류: '{region_name}'에서 '{sigungu_name}' 시군구를 찾을 수 없습니다.")
            return None

    return area_code, sigungu_code

def get_festivals_by_name(region_name: str, sigungu_name: Optional[str], event_start_date: str) -> Optional[List[Dict]]:
    if not TOUR_API_KEY:
        print("❌ [오류] .env 파일에 TOUR_API_KEY가 설정되지 않았습니다.")
        return None

    try:
        session = requests.Session()
        session.mount("https://", TlsAdapter())

        print("\n[과정 1] 지역명을 지역코드로 변환합니다...")
        codes = _fetch_and_find_codes(session, region_name, sigungu_name)

        if not codes:
            print("❌ [오류] 지역명->코드 변환 실패. 함수를 중단합니다.")
            return None

        area_code, sigungu_code = codes
        print(f"✅ [성공] 지역명 변환 완료: '{region_name}' -> areaCode={area_code}, '{sigungu_name or '전체'}' -> sigunguCode={sigungu_code or '(전체검색)'}")

        params = {
            "serviceKey": TOUR_API_KEY,
            "MobileOS": "ETC",
            "MobileApp": "NamdoBot",
            "_type": "json",
            "areaCode": area_code,
            "eventStartDate": event_start_date,
        }
        if sigungu_code:
            params["sigunguCode"] = sigungu_code

        print("\n[과정 2] 변환된 코드로 축제 정보를 검색합니다...")
        print(f"  - 요청 파라미터: {params}")
        response = session.get(FESTIVAL_API_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        items = data.get("response", {}).get("body", {}).get("items", {}).get("item", [])

        print(f"✅ [성공] 축제 정보 조회 완료. {len(items) if items else 0}개의 결과를 받았습니다.")

        if not items:
            return []

        return [{"title": item.get("title"), "addr1": item.get("addr1"), "start_date": item.get("eventstartdate"), "end_date": item.get("eventenddate"), "image": item.get("firstimage", "https://via.placeholder.com/300x200.png?text=No+Image"), "tel": item.get("tel")} for item in items]
    except requests.exceptions.RequestException as e:
        print(f"❌ [오류] API 호출에 실패했습니다: {e}")
        return None
    except json.JSONDecodeError:
        print("❌ [오류] API 응답이 JSON 형식이 아닙니다!")
        print(f"  - 서버 원본 응답 내용: {response.text}")
        return None
