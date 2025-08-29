# honam_festivals_to_csv.py

import csv
from datetime import datetime
from tour_api import TOUR_API_KEY, FESTIVAL_API_URL, _fetch_and_find_codes, TlsAdapter
import requests
import json

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
                "addr1": item.get("addr1"),
                "start_date": item.get("eventstartdate"),
                "end_date": item.get("eventenddate"),
                "image": item.get("firstimage", "https://via.placeholder.com/300x200.png?text=No+Image"),
                "tel": item.get("tel"),
            }
            for item in items
        ]
    except (requests.RequestException, json.JSONDecodeError) as e:
        print(f"❌ [오류] 축제 조회 실패: {e}")
        return []


def get_all_honam_festivals():
    """전북특별자치도 / 전라남도 / 광주 축제를 오늘 이후 기준으로 모두 가져옴"""
    today = datetime.today().strftime("%Y%m%d")
    regions = ["전북특별자치도", "전라남도", "광주"]

    all_results = []
    for region in regions:
        festivals = get_festivals_by_name(region_name=region, sigungu_name=None, event_start_date=today)
        if festivals:
            for f in festivals:
                f["region"] = region
            all_results.extend(festivals)

    return all_results


def save_to_csv(festivals, filename="honam_festivals.csv"):
    """축제 데이터를 CSV로 저장"""
    if not festivals:
        print("⚠️ 저장할 축제 데이터가 없습니다.")
        return

    keys = ["region", "title", "addr1", "start_date", "end_date", "tel", "image"]
    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(festivals)

    print(f"✅ {filename} 파일로 저장 완료! (총 {len(festivals)}건)")


if __name__ == "__main__":
    results = get_all_honam_festivals()
    save_to_csv(results)
