from fastapi import FastAPI, APIRouter, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

# FastAPI 설정
app = FastAPI()

origins = [
    "http://localhost:5000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 스키마
class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    answer: str

# Jinja2 Templates
templates = Jinja2Templates(directory="06_templates")

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# RAG 추가
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
embeddings = ClovaXEmbeddings(model="clir-emb-dolphin")
vectorstore = FAISS.from_documents(texts, embedding=embeddings)
retriever = vectorstore.as_retriever()

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
    chain_type_kwargs={"prompt": prompt}
)

# 라우터
router = APIRouter(prefix="/api")

@router.post("/chat", response_model=ChatResponse)
async def gen_answer(req: ChatRequest):
    print(f"입력: {req.query}")
    # TODO 부분에 RAG 호출 삽입
    result = qa_chain.invoke({"query": req.query})
    answer = result.get("result") or result.get("output_text") or ""
    return {"answer": answer}

# 라우터 등록
app.include_router(router)

# 실행
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)

# 갈비찜이 언제 나와요?