import os
import requests
from dotenv import load_dotenv, find_dotenv
from typing import List, Dict
from langchain.schema import Document


_ = load_dotenv(find_dotenv())
clova_api_key = os.getenv("CLOVASTUDIO_API_KEY")
service_key = os.getenv("PUBLIC_DATA_SERVICE_KEY")

def load_data_from_api(api_url: str, headers: Dict = None, params: Dict = None) -> List[Document]:
    
    #공공데이터포털 - 반려동물 여행 정보를 LangChain Document 객체로 변환
    
    # try:
    response = requests.get(api_url, headers=headers, params=params)
    # print(response.content) #
    response.raise_for_status()
    items = response.json().get('response', {}).get('body', {}).get('items', {}).get('item', [])
    for item in items:
        print(item)
    
    
    # if params.get("_type") == "json":
    #     data = response.json()
    #     print(1)
    # else:
    #     # XML 파싱이 필요한 경우
    #     import xml.etree.ElementTree as ET
        
    #     response.encoding = 'euc-kr'   # 한글 깨짐 방지
        
    #     root = ET.fromstring(response.text)
    #     text = response.text.strip()
        
    #     # XML을 딕셔너리로 변환하는 로직 추가 필요
    #     print(2)
    
    # documents = []
    
    # 공공데이터 일반적인 응답 구조: response > body > items > item[]
    if isinstance(response.content, dict):
        # 응답 구조에 따른 데이터 추출
        print(3)
        items = []
        if 'response' in response:
            response_data = response['response']
            print("reponse_data성공")
            if 'body' in response_data:
                body = response_data['body']
                print("body성공")
                if 'items' in body:
                    items_data = body['items']
                    print("items_data성공")
                    if isinstance(items_data, dict) and 'item' in items_data:
                        items = items_data['item']
                    elif isinstance(items_data, list):
                        items = items_data
        
        # items가 리스트가 아닌 경우 리스트로 변환
        if not isinstance(items, list):
            items = [items] if items else []




API_URL = "http://apis.data.go.kr/B551011/KorService2/detailPetTour2"
API_HEADERS = {} 

# 공공데이터 포털(한국관광공사)
API_PARAMS = {
    "serviceKey": service_key,
    "pageNo": 1,
    "numOfRows": 10,
    "MobileOS": "WEB",
    "MobileApp": "Flova_RAG_System_Test",
    "_type": "json"  # 또는 xml
}

# 5) 문서 로드
documents = load_data_from_api(API_URL, API_HEADERS, API_PARAMS)