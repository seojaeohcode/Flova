import csv
from datetime import datetime
from typing import Dict
from tour_api import TOUR_API_KEY, FESTIVAL_API_URL, KOR_SERVICE_URL,_fetch_and_find_codes, TlsAdapter
import requests
import json

def fetch_detail_common(content_id: str, content_type_id: str) -> Dict:
    """
    TourAPI의 detailCommon2를 호출하여 공통 정보를 가져오는 함수 (주로 '개요' 정보)
    """
    session = requests.Session()
    session.mount("https://", TlsAdapter())

    params = {
        "serviceKey": TOUR_API_KEY,
        "MobileOS": "ETC",
        "MobileApp": "NamdoBot",
        "_type": "json",
        "contentId": content_id,
    }

    try:
        response = session.get(f"{KOR_SERVICE_URL}/detailCommon2", params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        items = data.get("response", {}).get("body", {}).get("items", {})
        item = items.get("item", [{}])[0]
        return {
            "title": item.get("title", ""), # 축제명
            "createdtime": item.get("createdtime", ""), # 데이터 생성일
            "modifiedtime": item.get("modifiedtime", ""), # 데이터 수정일
            "tel": item.get("tel", ""), # 연락처
            "telname": item.get("telname", ""), # 연락처명
            "homepage": item.get("homepage", ""), # 홈페이지 URL
            "firstimage": item.get("firstimage", ""), # 대표 이미지 URL
            "firstimage2": item.get("firstimage2", ""), # 추가 이미지 URL
            "addr1": item.get("addr1", ""), # 주소
            "addr2": item.get("addr2", ""), # 상세주소
            "mapx": item.get("mapx", ""), # 경도
            "mapy": item.get("mapy", ""), # 위도
            "mlevel": item.get("mlevel", ""), # 지도 레벨
            "overview": item.get("overview", ""), # 개요
        }
    except (requests.RequestException, json.JSONDecodeError) as e:
        print(f"⚠️ [Common Info Error] contentId: {content_id}, Error: {e}")
        return {}

def fetch_detail_intro(content_id: str, content_type_id: str) -> Dict:
    """
    TourAPI의 detailIntro2를 호출하여 축제 소개 정보를 가져오는 함수
    """
    session = requests.Session()
    session.mount("https://", TlsAdapter())

    params = {
        "serviceKey": TOUR_API_KEY,
        "MobileOS": "ETC",
        "MobileApp": "NamdoBot",
        "_type": "json",
        "contentId": content_id,
        "contentTypeId": content_type_id,
    }

    try:
        response = session.get(f"{KOR_SERVICE_URL}/detailIntro2", params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        items = data.get("response", {}).get("body", {}).get("items", {})
        item = items.get("item", [{}])[0]
        return {
            "sponsor1": item.get("sponsor1", ""), # 주최자 정보
            "sponsor1tel": item.get("sponsor1tel", ""), # 주최자 연락처
            "sponsor2": item.get("sponsor2", ""), # 주관사 정보
            "eventenddate": item.get("eventenddate", ""), # 축제 종료일
            "playtime": item.get("playtime", ""), # 관람 소요 시간
            "eventplace": item.get("eventplace", ""), # 축제 장소
            "eventstartdate": item.get("eventstartdate", ""), # 축제 시작일
            "usetimefestival": item.get("usetimefestival", ""), # 축제 이용 시간
            "progresstype": item.get("progresstype", ""), # 행사 진행 유형
            "festivaltype": item.get("festivaltype", ""), # 축제 유형
        }
    except (requests.RequestException, json.JSONDecodeError) as e:
        print(f"⚠️ [Intro Info Error] contentId: {content_id}, Error: {e}")
        return {}

def fetch_pet_info(content_id: str) -> Dict:
    """
    TourAPI의 detailPetTour2를 호출하여 반려동물 여행 정보를 가져오는 함수
    """
    session = requests.Session()
    session.mount("https://", TlsAdapter())

    params = {
        "serviceKey": TOUR_API_KEY,
        "MobileOS": "ETC",
        "MobileApp": "NamdoBot",
        "_type": "json",
        "contentId": content_id,
    }

    try:
        response = session.get(f"{KOR_SERVICE_URL}/detailPetTour2", params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        # print(data)
        items = data.get("response", {}).get("body", {}).get("items", {})

        if not isinstance(items, dict):
            item = {}
        else:
            item = items.get("item", [])
        
        # item이 리스트인 경우 첫 번째 항목을 사용
        if isinstance(item, list) and item:
            item = item[0]
        elif not isinstance(item, dict):
            item = {}

        # 반려동물 정보가 없는 경우 빈 딕셔너리 반환
        if not item:
            return {}

        return {
            "acmpyPsblCpam": item.get("acmpyPsblCpam", ""),  # 동반 가능 동물
            "relaRntlPrdlst": item.get("relaRntlPrdlst", ""),  # 관련 렌탈 품목
            "acmpyNeedMtr": item.get("acmpyNeedMtr", ""),  # 동반 시 필요 사항
            "relaFrnshPrdlst": item.get("relaFrnshPrdlst", ""),  # 관련 대여 품목
            "etcAcmpyInfo": item.get("etcAcmpyInfo", ""),  # 기타 동반 정보
            "relaPurcPrdlst": item.get("relaPurcPrdlst", ""),  # 관련 구매 품목
            "relaAcdntRiskMtr": item.get("relaAcdntRiskMtr", ""),  # 관련 사고 대비 사항
            "acmpyTypeCd": item.get("acmpyTypeCd", ""),  # 동반 유형 코드 (동반 구분)
            "relaPosesFclty": item.get("relaPosesFclty", ""),  # 관련 구비 시설
        }
    except (requests.RequestException, json.JSONDecodeError):
        # API 호출 실패 시 빈 딕셔너리 반환
        return {}

def fetch_all_festivals(area_code, sigungu_code, event_start_date):
    """페이지네이션을 돌면서 모든 축제 데이터를 가져오기"""
    session = requests.Session()
    session.mount("https://", TlsAdapter())

    all_items = []
    page = 1

    while True:
        params = {
            "serviceKey": TOUR_API_KEY,
            "MobileOS": "ETC",
            "MobileApp": "NamdoBot",
            "_type": "json",
            "areaCode": area_code,
            "eventStartDate": event_start_date,
            "numOfRows": 1000,
            "pageNo": page,
        }
        if sigungu_code:
            params["sigunguCode"] = sigungu_code

        response = session.get(FESTIVAL_API_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        body = data.get("response", {}).get("body", {})
        items = body.get("items", {}).get("item", [])
        total_count = body.get("totalCount", 0)

        all_items.extend(items)

        if len(all_items) >= total_count:
            break
        page += 1

    return all_items


def get_festivals_by_name(region_name: str, sigungu_name: str, event_start_date: str):
    """지역명과 날짜를 받아 모든 축제 정보 가져오기 (페이지네이션 적용)"""
    try:
        session = requests.Session()
        session.mount("https://", TlsAdapter())

        codes = _fetch_and_find_codes(session, region_name, sigungu_name)
        if not codes:
            print(f"❌ [오류] '{region_name}' 지역 코드 변환 실패")
            return []

        area_code, sigungu_code = codes

        items = fetch_all_festivals(area_code, sigungu_code, event_start_date)

        return [
            {
                "title": item.get("title"),
                "contentid": item.get("contentid"),
                "contenttypeid": item.get("contenttypeid"),
                "addr1": item.get("addr1"),
                "start_date": item.get("eventstartdate"),
                "end_date": item.get("eventenddate"),
                "image": item.get("firstimage", "https://via.placeholder.com/300x200.png?text=No+Image"),
                "progresstype": item.get("progresstype"),
                "festivaltype": item.get("festivaltype"),
                "tel": item.get("tel"),
            }
            for item in items
        ]
    except (requests.RequestException, json.JSONDecodeError) as e:
        print(f"❌ [오류] 축제 조회 실패: {e}")
        return []


def get_all_honam_festivals():
    """
    호남 지역 축제 정보를 가져와 기본+반려동물, 공통(개요), 소개 정보로 분리하여 반환합니다.
    """
    today = datetime.today().strftime("%Y%m%d")
    regions = ["전북특별자치도", "전라남도", "광주"]

    # 1. 세 종류의 데이터를 담을 빈 리스트를 각각 준비합니다.
    base_festivals = []
    common_details = []
    intro_details = []

    for region in regions:
        print(f"\n--- {region} 지역 축제 정보 수집 시작 ---")
        festivals = get_festivals_by_name(region_name=region, sigungu_name=None, event_start_date=today)
        
        if not festivals:
            print(f"--- {region} 지역에 예정된 축제가 없습니다. ---")
            continue

        for i, f in enumerate(festivals):
            print(f"({i+1}/{len(festivals)}) '{f.get('title', f.get('contentid'))}' 상세 정보 조회 중...")
            content_id = f["contentid"]
            content_type_id = f["contenttypeid"]
            
            # --- API 호출 ---
            pet_info = fetch_pet_info(content_id)
            detail_common = fetch_detail_common(content_id, content_type_id)
            detail_intro = fetch_detail_intro(content_id, content_type_id)

            # --- 2. 데이터 분리하여 각 리스트에 추가 ---
            # (1) 기본 정보 + 반려동물 정보
            base_info = f.copy() # 원본 기본 정보를 복사
            base_info["region"] = region
            base_info.update(pet_info) # 반려동물 정보 합치기
            base_festivals.append(base_info)

            # (2) 공통 정보 (개요 등)
            common_info = detail_common.copy()
            common_info["contentid"] = content_id # 데이터 연결을 위한 ID 추가
            common_details.append(common_info)

            # (3) 소개 정보 (이용 시간, 요금 등)
            intro_info = detail_intro.copy()
            intro_info["contentid"] = content_id # 데이터 연결을 위한 ID 추가
            intro_details.append(intro_info)

    # 3. 3개의 분리된 리스트를 반환합니다.
    return base_festivals, common_details, intro_details


def save_base_csv(festivals, filename="honam_festivals_base.csv"):
    """기본 축제 정보와 반려동물 정보를 CSV로 저장"""
    if not festivals:
        print(f"⚠️ {filename}에 저장할 데이터가 없습니다.")
        return
    # 기본 정보와 반려동물 정보에 맞는 키 목록
    keys = [
        "region", "contentid", "title", "addr1", "start_date", "end_date", "tel", "image", 
        "progresstype", "festivaltype", # 기본 정보에 있던 키 추가
        "acmpyPsblCpam", "relaRntlPrdlst", "relaFrnshPrdlst", "acmpyNeedMtr", "etcAcmpyInfo", 
        "relaPurcPrdlst", "relaAcdntRiskMtr", "acmpyTypeCd", "relaPosesFclty"
    ]
    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        # extrasaction='ignore'는 딕셔너리에 키 목록 외의 키가 있어도 무시하고 저장하게 해줍니다.
        writer = csv.DictWriter(f, fieldnames=keys, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(festivals)
    print(f"✅ {filename} 파일로 저장 완료! (총 {len(festivals)}건)")

def save_common_csv(details, filename="honam_festivals_common.csv"):
    """축제 공통 정보(개요)를 CSV로 저장"""
    if not details:
        print(f"⚠️ {filename}에 저장할 데이터가 없습니다.")
        return
    # Common 정보에 맞는 키 목록
    keys = [
        "contentid", "title", "createdtime", "modifiedtime", "tel", "telname",
        "homepage", "firstimage", "firstimage2", "addr1", "addr2",
        "mapx", "mapy", "mlevel", "overview"
    ]
    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=keys, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(details)
    print(f"✅ {filename} 파일로 저장 완료! (총 {len(details)}건)")

def save_intro_csv(details, filename="honam_festivals_intro.csv"):
    """축제 소개 정보(이용 정보)를 CSV로 저장"""
    if not details:
        print(f"⚠️ {filename}에 저장할 데이터가 없습니다.")
        return
    # Intro 정보에 맞는 키 목록
    keys = [
        "contentid", "sponsor1", "sponsor1tel", "sponsor2", "eventenddate",
        "playtime", "eventplace", "eventstartdate", "usetimefestival",
        "progresstype", "festivaltype"
    ]
    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=keys, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(details)
    print(f"✅ {filename} 파일로 저장 완료! (총 {len(details)}건)")


if __name__ == "__main__":
    # get_all_honam_festivals 함수로부터 3개의 분리된 리스트를 각각 전달받습니다.
    base_data, common_data, intro_data = get_all_honam_festivals()
    
    # 각 데이터를 별도의 파일로 저장하는 함수를 각각 호출합니다.
    save_base_csv(base_data)
    save_common_csv(common_data)
    save_intro_csv(intro_data)