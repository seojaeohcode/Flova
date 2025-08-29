import os
from dotenv import load_dotenv, find_dotenv
from langchain.schema.runnable import RunnablePassthrough
from langchain_naver import ChatClovaX
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferWindowMemory

# 1. 환경변수 불러오기
_ = load_dotenv(find_dotenv())
api_key = os.getenv("CLOVASTUDIO_API_KEY")

# 2. LLM 생성
llm = ChatClovaX(
    model="HCX-007",
    api_key=api_key,
    temperature=0.2,
)

# 3. Memory 생성
memory = ConversationBufferWindowMemory(
    k=4,                              # 최근 4턴 유지
    memory_key="chat_history",
    return_messages=True,
)

# 4. 메모리 불러오기
def load_memory(_input):
    return memory.load_memory_variables({})["chat_history"]

# 5. 프롬프트 작성
system_prompt = """
    당신은 친절한 인공지능 비서입니다.
    당신에게 문서와 질문이 주어질 것이며,
    항상 한국어로 정확하고 간결하게 답변해야 합니다.
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{query}"),
])

# 6. 체인 구성
chain = RunnablePassthrough.assign(chat_history=load_memory) | prompt | llm

# 7. 대화 루프
try:
    while True:
        query = input("질문: ").strip()
        if query.lower() == "q":
            break

        result = chain.invoke({"query": query})
        answer = getattr(result, "content", str(result))
        print(f"답변: {answer}")

        # 대화 저장
        memory.save_context({"input": query}, {"output": answer})

        # 현재 대화/요약 확인(옵션)
        print(memory.load_memory_variables({})["chat_history"])

except KeyboardInterrupt:
    print("\n종료합니다.")

# 네이버 클라우드 플랫폼에 대해 설명해주세요.