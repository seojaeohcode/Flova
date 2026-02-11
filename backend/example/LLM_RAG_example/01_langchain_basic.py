import os
from dotenv import load_dotenv, find_dotenv
from langchain_naver import ChatClovaX
from langchain.prompts import ChatPromptTemplate

# 1. 환경변수 불러오기
_ = load_dotenv(find_dotenv())
api_key=os.getenv("CLOVASTUDIO_API_KEY")

# 2. LLM 생성
llm = ChatClovaX(
    model="HCX-007",
    api_key=api_key,
    temperature=0.2,
)

# 3. 프롬프트 생성
system_prompt = """
    당신은 친절한 인공지능 비서입니다.
    당신에게 문서와 질문이 주어질 것이며,
    항상 한국어로 정확하고 간결하게 답변해야 합니다.
"""
prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{query}")
])

# 4. Chain 생성
chain = prompt | llm

# 5. Chain 실행
question = "HyperCLOVA에 대해 설명해주세요."
result = chain.invoke({"query": question})
print(result.content)
