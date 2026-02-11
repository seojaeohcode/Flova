import os
from dotenv import load_dotenv, find_dotenv
from langchain_naver import ChatClovaX, ClovaXEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain.prompts import ChatPromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA

# 1) env
_ = load_dotenv(find_dotenv())
api_key = os.getenv("CLOVASTUDIO_API_KEY")

# 2) LLM
llm = ChatClovaX(model="HCX-007", api_key=api_key, temperature=0.2)

# 3) 문서 로드
pdf_path = "일주일 식단.pdf"
loader = PyPDFLoader(pdf_path)
documents = loader.load()

# 4) 청크 분할
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=250, chunk_overlap=40,
    separators=["\n\n", "\n", " ", ""],
)
texts = text_splitter.split_documents(documents)
texts = [d for d in texts if len(d.page_content) <= 512]
if not texts:
    raise ValueError("분할된 텍스트가 없습니다. PDF/경로를 확인하세요.")

# 5) 임베딩/벡터 DB
embeddings = ClovaXEmbeddings(model="clir-emb-dolphin", api_key=api_key)
vectorstore = FAISS.from_documents(texts, embedding=embeddings) #FAISS: 벡터

retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

# 6) 프롬프트
system_prompt = """
    당신은 지식검색시스템입니다.
    다음 질문에 대해 제공된 문서를 바탕으로 정확하고 간결하게 한국어로 답변하세요.
    제공된 문서 이외의 내용은 "답변이 어렵습니다."라고 답하세요.

    문서 내용:
    {context}
"""
prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{question}"),
])

# 7) 체인
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    return_source_documents=True,
    chain_type_kwargs={"prompt": prompt},  # ← {question} 사용 프롬프트
)

# 8) 질의 루프
while True:
    query = input("질문: ")
    if query.lower().strip() == "q":
        break
    # RetrievalQA는 입력 키로 "query"를 사용
    result = qa_chain.invoke({"query": query})
    answer = result.get("result") or result.get("output_text") or ""
    print(f"답변: {answer}")

# 8월 28일 저녁 메뉴를 알려주세요.