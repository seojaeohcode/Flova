import os
import requests
import getpass
import json
from dotenv import load_dotenv, find_dotenv
from langchain_naver import ChatClovaX, ClovaXEmbeddings
from langchain.prompts import ChatPromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.schema import Document
from langchain_core.output_parsers import StrOutputParser
from typing import List, Dict, Any

output_parser = StrOutputParser()

# 1) env
_ = load_dotenv(find_dotenv())
clova_api_key = os.getenv("CLOVASTUDIO_API_KEY")
service_key = os.getenv("PUBLIC_DATA_SERVICE_KEY")

# 2) LLM
llm = ChatClovaX(model="HCX-007", api_key=clova_api_key, temperature=0.2)

# 3) API에서 데이터 불러오기: API 응답을 LangChain Document 형태로 변환하기 위함
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
    #     for i, item in enumerate(items):
    #         if isinstance(item, dict):
    #             # 여행지 정보를 문서로 변환
    #             content_parts = []
    #             metadata = {"source": f"tour_item_{i}"}
                
    #             # 주요 필드들을 content로 구성 (실제 API 응답 필드에 맞게 조정 필요)
    #             field_mappings = {
    #                 'title': '제목',
    #                 'addr1': '주소',
    #                 'addr2': '상세주소', 
    #                 'tel': '전화번호',
    #                 'overview': '개요',
    #                 'homepage': '홈페이지',
    #                 'contentTypeId': '콘텐츠타입',
    #                 'areaCode': '지역코드',
    #                 'sigunguCode': '시군구코드',
    #                 'cat1': '대분류',
    #                 'cat2': '중분류',
    #                 'cat3': '소분류'
    #             }
                
    #             for api_field, korean_name in field_mappings.items():
    #                 if api_field in item and item[api_field]:
    #                     content_parts.append(f"{korean_name}: {item[api_field]}")
    #                     metadata[api_field] = item[api_field]
                
    #             # 모든 원본 데이터를 메타데이터에 저장
    #             for key, value in item.items():
    #                 if key not in metadata:
    #                     metadata[key] = value
                
    #             if content_parts:
    #                 doc = Document(
    #                     page_content="\n".join(content_parts),
    #                     metadata=metadata
    #                 )
    #                 documents.append(doc)
    
    # print(f"API에서 {len(documents)}개 여행지 정보를 로드했습니다.")
    # return documents
        
    # except requests.RequestException as e:
    #     print(f"API 호출 오류: {e}")
    #     return []
    # except json.JSONDecodeError as e:
    #     print(f"JSON 파싱 오류: {e}")
    #     return []
    # except Exception as e:
    #     print(f"데이터 로드 오류: {e}")
    #     return []


# 4) API 설정 - 공공데이터포털 반려동물 동반 여행 정보
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

if not documents:
    raise ValueError("API에서 데이터를 불러오지 못했습니다. API URL과 설정을 확인하세요.")

# 6) 청크 분할
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=250, 
    chunk_overlap=40,
    separators=["\n\n", "\n", " ", ""],
)
texts = text_splitter.split_documents(documents)
texts = [d for d in texts if len(d.page_content) <= 512]

if not documents:
    raise ValueError("분할된 텍스트가 없습니다. API 데이터를 확인하세요.")

print(f"총 {len(texts)}개의 텍스트 청크가 생성되었습니다.")

# 7) 임베딩/벡터 DB
StrOutputParser
embeddings = ClovaXEmbeddings(model="clir-emb-dolphin", api_key=api_key)
vectorstore = FAISS.from_documents(texts, embedding=embeddings)



retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

# 8) 프롬프트
system_prompt = """
    당신은 반려동물 동반 여행 전문 상담사입니다.
    다음 질문에 대해 제공된 여행지 정보를 바탕으로 정확하고 간결하게 한국어로 답변하세요.
    반려동물과 함께 갈 수 있는 여행지, 숙박시설, 관광명소 등의 정보를 제공합니다.
    제공된 문서 이외의 내용은 "해당 정보가 없습니다."라고 답하세요.

    여행지 정보:
    {context}
"""
prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{question}"),
])

# 9) 체인
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    return_source_documents=True,
    chain_type_kwargs={"prompt": prompt},
)

# 10) 질의 루프
print("반려동물 동반 여행 정보 RAG 시스템이 준비되었습니다!")
print("예시 질문: '서울에서 반려동물과 갈 수 있는 축제는?', '부산 애견 동반 숙소 추천해줘'")
while True:
    query = input("질문: ")
    if query.lower().strip() == "q":
        break
        
    result = qa_chain.invoke({"query": query})
    answer = result.get("result") or result.get("output_text") or ""
    print(f"답변: {answer}")
    
    # 소스 문서 확인 (옵션)
    if "source_documents" in result:
        print(f"\n참조된 여행지 개수: {len(result['source_documents'])}")
        for i, doc in enumerate(result["source_documents"][:2]):  # 상위 2개만 표시
            print(f"여행지 {i+1}: {doc.page_content[:100]}...")
            if 'title' in doc.metadata:
                print(f"  - 제목: {doc.metadata['title']}")
            if 'addr1' in doc.metadata:
                print(f"  - 주소: {doc.metadata['addr1']}")