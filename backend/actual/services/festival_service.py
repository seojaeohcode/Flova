import os
import csv
import requests
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv
import ssl
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager

from core.database import get_db, Festival, FestivalDetail, FestivalIntro, PetInfo
from crud import create_festival, create_festival_detail, create_festival_intro, create_pet_info

load_dotenv()

TOUR_API_KEY = os.getenv("TOUR_API_KEY")
KOR_SERVICE_URL = "https://apis.data.go.kr/B551011/KorService2"
FESTIVAL_API_URL = f"{KOR_SERVICE_URL}/searchFestival2"
AREA_CODE_API_URL = f"{KOR_SERVICE_URL}/areaCode2"

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

class FestivalService:
    def __init__(self):
        self.session = requests.Session()
        self.session.mount("https://", TlsAdapter())
        self._area_code_cache = {}

    def _fetch_codes(self, area_code: str = "") -> Optional[List[Dict]]:
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
            response = self.session.get(AREA_CODE_API_URL, params=params, timeout=5)
            response.raise_for_status()
            items = response.json().get("response", {}).get("body", {}).get("items", {}).get("item", [])
            return items
        except requests.RequestException as e:
            print(f"❌ areaCode API 호출 실패: {e}")
            return None

    def _fetch_and_find_codes(self, region_name: str, sigungu_name: Optional[str] = None) -> Optional[Tuple[str, str]]:
        if "main_areas" not in self._area_code_cache:
            main_areas = self._fetch_codes()
            if main_areas is None:
                return None
            self._area_code_cache["main_areas"] = {item['name']: item['code'] for item in main_areas}

        area_code = self._area_code_cache["main_areas"].get(region_name)
        if not area_code:
            print(f"오류: '{region_name}' 광역 지역을 찾을 수 없습니다.")
            return None

        sigungu_code = ""
        if sigungu_name:
            cache_key = f"sigungu_{area_code}"
            if cache_key not in self._area_code_cache:
                sigungu_areas = self._fetch_codes(area_code=area_code)
                if sigungu_areas is None:
                    return None
                self._area_code_cache[cache_key] = {item['name']: item['code'] for item in sigungu_areas}

            sigungu_code = self._area_code_cache[cache_key].get(sigungu_name)
            if sigungu_code is None:
                print(f"오류: '{region_name}'에서 '{sigungu_name}' 시군구를 찾을 수 없습니다.")
                return None

        return area_code, sigungu_code

    def fetch_detail_common(self, content_id: str, content_type_id: str) -> Dict:
        params = {
            "serviceKey": TOUR_API_KEY,
            "MobileOS": "ETC",
            "MobileApp": "NamdoBot",
            "_type": "json",
            "contentId": content_id,
        }
        try:
            response = self.session.get(f"{KOR_SERVICE_URL}/detailCommon2", params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            items = data.get("response", {}).get("body", {}).get("items", {})
            item = items.get("item", [{}])[0]
            return {
                "title": item.get("title", ""),
                "createdtime": item.get("createdtime", ""),
                "modifiedtime": item.get("modifiedtime", ""),
                "tel": item.get("tel", ""),
                "telname": item.get("telname", ""),
                "homepage": item.get("homepage", ""),
                "firstimage": item.get("firstimage", ""),
                "firstimage2": item.get("firstimage2", ""),
                "addr1": item.get("addr1", ""),
                "addr2": item.get("addr2", ""),
                "mapx": item.get("mapx", ""),
                "mapy": item.get("mapy", ""),
                "mlevel": item.get("mlevel", ""),
                "overview": item.get("overview", ""),
            }
        except (requests.RequestException, json.JSONDecodeError) as e:
            print(f"⚠️ [Common Info Error] contentId: {content_id}, Error: {e}")
            return {}

    def fetch_detail_intro(self, content_id: str, content_type_id: str) -> Dict:
        params = {
            "serviceKey": TOUR_API_KEY,
            "MobileOS": "ETC",
            "MobileApp": "NamdoBot",
            "_type": "json",
            "contentId": content_id,
            "contentTypeId": content_type_id,
        }
        try:
            response = self.session.get(f"{KOR_SERVICE_URL}/detailIntro2", params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            items = data.get("response", {}).get("body", {}).get("items", {})
            item = items.get("item", [{}])[0]
            return {
                "sponsor1": item.get("sponsor1", ""),
                "sponsor1tel": item.get("sponsor1tel", ""),
                "sponsor2": item.get("sponsor2", ""),
                "eventenddate": item.get("eventenddate", ""),
                "playtime": item.get("playtime", ""),
                "eventplace": item.get("eventplace", ""),
                "eventstartdate": item.get("eventstartdate", ""),
                "usetimefestival": item.get("usetimefestival", ""),
                "progresstype": item.get("progresstype", ""),
                "festivaltype": item.get("festivaltype", ""),
            }
        except (requests.RequestException, json.JSONDecodeError) as e:
            print(f"⚠️ [Intro Info Error] contentId: {content_id}, Error: {e}")
            return {}

    def fetch_pet_info(self, content_id: str) -> Dict:
        params = {
            "serviceKey": TOUR_API_KEY,
            "MobileOS": "ETC",
            "MobileApp": "NamdoBot",
            "_type": "json",
            "contentId": content_id,
        }
        try:
            response = self.session.get(f"{KOR_SERVICE_URL}/detailPetTour2", params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            items = data.get("response", {}).get("body", {}).get("items", {})

            if not isinstance(items, dict):
                item = {}
            else:
                item = items.get("item", [])

            if isinstance(item, list) and item:
                item = item[0]
            elif not isinstance(item, dict):
                item = {}

            if not item:
                return {}

            return {
                "acmpyPsblCpam": item.get("acmpyPsblCpam", ""),
                "relaRntlPrdlst": item.get("relaRntlPrdlst", ""),
                "acmpyNeedMtr": item.get("acmpyNeedMtr", ""),
                "etcAcmpyInfo": item.get("etcAcmpyInfo", ""),
                "relaPurcPrdlst": item.get("relaPurcPrdlst", ""),
                "relaAcdntRiskMtr": item.get("relaAcdntRiskMtr", ""),
                "acmpyTypeCd": item.get("acmpyTypeCd", ""),
                "relaPosesFclty": item.get("relaPosesFclty", ""),
            }
        except (requests.RequestException, json.JSONDecodeError):
            return {}

    def fetch_all_festivals(self, area_code, sigungu_code, event_start_date):
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

            response = self.session.get(FESTIVAL_API_URL, params=params, timeout=10)
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

    def get_festivals_by_name(self, region_name: str, sigungu_name: str, event_start_date: str):
        try:
            codes = self._fetch_and_find_codes(region_name, sigungu_name)
            if not codes:
                print(f"❌ [오류] '{region_name}' 지역 코드 변환 실패")
                return []

            area_code, sigungu_code = codes
            items = self.fetch_all_festivals(area_code, sigungu_code, event_start_date)

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

    def collect_all_honam_festivals(self, db):
        today = datetime.today().strftime("%Y%m%d")
        regions = ["전북특별자치도", "전라남도", "광주"]
        total_collected = 0

        for region in regions:
            print(f"\n--- {region} 지역 축제 정보 수집 시작 ---")
            festivals = self.get_festivals_by_name(region_name=region, sigungu_name=None, event_start_date=today)

            if not festivals:
                print(f"--- {region} 지역에 예정된 축제가 없습니다. ---")
                continue

            for i, f in enumerate(festivals):
                print(f"({i+1}/{len(festivals)}) '{f.get('title', f.get('contentid'))}' 상세 정보 조회 중...")
                content_id = f["contentid"]
                content_type_id = f["contenttypeid"]

                pet_info = self.fetch_pet_info(content_id)
                detail_common = self.fetch_detail_common(content_id, content_type_id)
                detail_intro = self.fetch_detail_intro(content_id, content_type_id)

                try:
                    festival_data = f.copy()
                    festival_data["region"] = region
                    create_festival(db, festival_data)

                    if detail_common:
                        detail_common["contentid"] = content_id
                        create_festival_detail(db, detail_common)

                    if detail_intro:
                        detail_intro["contentid"] = content_id
                        create_festival_intro(db, detail_intro)

                    if pet_info:
                        pet_info["contentid"] = content_id
                        create_pet_info(db, pet_info)

                    total_collected += 1
                    print(f"✅ '{f.get('title')}' 저장 완료")

                except Exception as e:
                    print(f"❌ '{f.get('title')}' 저장 실패: {e}")

        print(f"\n🎉 총 {total_collected}개의 축제 정보 수집 완료!")
        return total_collected

    def get_festival_recommendations(self, db, travel_period: str, companion_type: str,
                                   atmosphere: str, core_experience: str,
                                   additional_considerations: str) -> List[Dict]:
        festivals = db.query(Festival).filter(
            Festival.start_date >= travel_period
        ).all()

        recommendations = []
        for festival in festivals:
            score = 0
            reasons = []

            if "전북" in festival.region or "전남" in festival.region or "광주" in festival.region:
                score += 10
                reasons.append("호남 지역 축제")

            if travel_period in festival.start_date or travel_period in festival.end_date:
                score += 15
                reasons.append("계절에 적합")

            if companion_type == "부모님 동반 가족":
                if "휴식" in atmosphere or "여유" in atmosphere:
                    score += 20
                    reasons.append("부모님과 함께하기 좋은 여유로운 분위기")

            if core_experience == "음식" and "음식" in str(festival.festivaltype):
                score += 25
                reasons.append("음식 중심 축제")

            if "걷기" in additional_considerations and "평지" in str(festival.progresstype):
                score += 15
                reasons.append("걷기 편한 평지 조성")

            if score > 30:
                recommendations.append({
                    "festival": festival,
                    "score": score,
                    "reasons": reasons
                })

        recommendations.sort(key=lambda x: x["score"], reverse=True)
        return recommendations[:5]


festival_service = FestivalService()
