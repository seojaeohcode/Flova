from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# FastAPI 앱 & CORS 설정
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

# 스키마 = 모델
class ChatRequest(BaseModel): # 서버 요청
    query: str

class ChatResponse(BaseModel): #서버 응답
    answer: str

# 라우터
router = APIRouter(prefix="/api")

@router.post("/chat", response_model=ChatResponse)
async def gen_answer(req: ChatRequest):
    print(f"입력: {req.query}")

    # TODO: 여기서 LLM/RAG 로직을 호출하여 답변 생성
    # ex) answer = qa_chain.invoke({"query": req.query})["result"]
    answer = ""

    return {"answer": answer}

# 라우터 등록
app.include_router(router)

# 실행 (개발용)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)


