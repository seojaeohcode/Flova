# import os
# import requests
# from dotenv import load_dotenv, find_dotenv
# from typing import List, Dict
# from langchain.schema import Document


# _ = load_dotenv(find_dotenv())
# clova_api_key = os.getenv("CLOVASTUDIO_API_KEY")
# service_key = os.getenv("PUBLIC_DATA_SERVICE_KEY")

# def load_data_from_api(api_url: str, headers: Dict = None, params: Dict = None) -> List[Document]:
    
#     #공공데이터포털 - 반려동물 여행 정보를 LangChain Document 객체로 변환
    
#     # try:
#     response = requests.get(api_url, headers=headers, params=params)
#     # print(response.content) #
#     response.raise_for_status()
#     items = response.json().get('response', {}).get('body', {}).get('items', {}).get('item', [])
#     for item in items:
#         print(item)
    
    
#     # if params.get("_type") == "json":
#     #     data = response.json()
#     #     print(1)
#     # else:
#     #     # XML 파싱이 필요한 경우
#     #     import xml.etree.ElementTree as ET
        
#     #     response.encoding = 'euc-kr'   # 한글 깨짐 방지
        
#     #     root = ET.fromstring(response.text)
#     #     text = response.text.strip()
        
#     #     # XML을 딕셔너리로 변환하는 로직 추가 필요
#     #     print(2)
    
#     # documents = []
    
#     # 공공데이터 일반적인 응답 구조: response > body > items > item[]
#     if isinstance(response.content, dict):
#         # 응답 구조에 따른 데이터 추출
#         print(3)
#         items = []
#         if 'response' in response:
#             response_data = response['response']
#             print("reponse_data성공")
#             if 'body' in response_data:
#                 body = response_data['body']
#                 print("body성공")
#                 if 'items' in body:
#                     items_data = body['items']
#                     print("items_data성공")
#                     if isinstance(items_data, dict) and 'item' in items_data:
#                         items = items_data['item']
#                     elif isinstance(items_data, list):
#                         items = items_data
        
#         # items가 리스트가 아닌 경우 리스트로 변환
#         if not isinstance(items, list):
#             items = [items] if items else []




# API_URL = "http://apis.data.go.kr/B551011/KorService2/detailPetTour2"
# API_HEADERS = {} 

# # 공공데이터 포털(한국관광공사)
# API_PARAMS = {
#     "serviceKey": service_key,
#     "pageNo": 1,
#     "numOfRows": 10,
#     "MobileOS": "WEB",
#     "MobileApp": "Flova_RAG_System_Test",
#     "_type": "json"  # 또는 xml
# }

# # 5) 문서 로드
# documents = load_data_from_api(API_URL, API_HEADERS, API_PARAMS)

# tour_api.py

import requests
import os
import json
from dotenv import load_dotenv
from typing import List, Dict, Optional, Tuple
import ssl
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager

# .env 파일 로드 및 변수 선언
load_dotenv()
TOUR_API_KEY = os.getenv("PUBLIC_DATA_SERVICE_KEY")

KOR_SERVICE_URL = "https://apis.data.go.kr/B551011/KorService2"
FESTIVAL_API_URL = f"{KOR_SERVICE_URL}/searchFestival2"
AREA_CODE_API_URL = f"{KOR_SERVICE_URL}/areaCode2"
_area_code_cache = {}

# SSL/TLS 호환성 문제 해결을 위한 어댑터 클래스
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
    """TourAPI의 areaCode2를 호출하여 지역/시군구 코드 목록을 가져오는 내부 함수"""
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
    """지역명으로 코드를 실시간 조회하는 함수 (캐시 기능 포함)"""
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
    """ TourAPI를 호출하여 특정 지역과 기간의 축제 정보를 가져옵니다. """
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

        # [수정] API 요청 파라미터를 최소한으로 간소화
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
        print(items)
        if not items:
            return []

        return [{"title": item.get("title"), "contentid": item.get("contentid"), "addr1": item.get("addr1"), "start_date": item.get("eventstartdate"), "end_date": item.get("eventenddate"), "image": item.get("firstimage", "https://via.placeholder.com/300x200.png?text=No+Image"), "tel": item.get("tel")} for item in items]
    except requests.exceptions.RequestException as e:
        print(f"❌ [오류] API 호출에 실패했습니다: {e}")
        return None
    except json.JSONDecodeError:
        print("❌ [오류] API 응답이 JSON 형식이 아닙니다!")
        print(f"  - 서버 원본 응답 내용: {response.text}")
        return None
    

if __name__ == '__main__':
    # 예시: '서울'의 '강남구'에서 열리는 축제를 2025년 5월 1일 이후로 검색
    region_name = "광주"
    sigungu_name = "서구"
    start_date = "20250501"

    print(f"[{region_name} {sigungu_name}의 축제를 검색합니다...]")
    festivals = get_festivals_by_name(region_name, sigungu_name, start_date)

    if festivals is None:
        print("검색에 실패했습니다.")
    elif not festivals:
        print("해당 조건에 맞는 축제가 없습니다.")
    else:
        print("\n🔍 검색 결과:")
        for festival in festivals:
            print("-" * 20)
            print(f"제목: {festival['title']}")
            print(f"주소: {festival['addr1']}")
            print(f"기간: {festival['start_date']} ~ {festival['end_date']}")
            print(f"전화번호: {festival['tel'] if festival['tel'] else '정보 없음'}")
            print(f"이미지: {festival['image']}")