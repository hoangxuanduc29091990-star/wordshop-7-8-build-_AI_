import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv
from contextlib import asynccontextmanager

load_dotenv()
# Use package-relative import so uvicorn can import when running as package
from .ai_engine import create_ai_engine

ai_engine = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global ai_engine
    ai_engine = create_ai_engine()
    if getattr(ai_engine, 'name', None) == 'mock':
        print("[Startup Warning] AI engine đang chạy ở chế độ mô phỏng (fallback).")
    yield

app = FastAPI(title="Gemini AI Assistant API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cấu hình đường dẫn tuyệt đối cho thư mục web tĩnh
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BACKEND_DIR)
EMBED_DIR = os.path.join(ROOT_DIR, "embed-widget")

if os.path.exists(EMBED_DIR):
    app.mount("/embed-widget", StaticFiles(directory=EMBED_DIR), name="embed-widget")
else:
    print(f"Cảnh báo: Không tìm thấy thư mục tĩnh tại {EMBED_DIR}")

class PageContext(BaseModel):
    url: str | None = None
    title: str | None = None

class ChatRequest(BaseModel):
    message: str
    page_context: PageContext | None = None

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    if not request.message:
        raise HTTPException(status_code=400, detail="Message không được để trống")
    if ai_engine is None:
        raise HTTPException(status_code=503, detail="AI engine không khả dụng. Thiết lập GEMINI_API_KEY để kích hoạt.")

    return StreamingResponse(
        ai_engine.generate_chat_stream(
            user_message=request.message,
            page_context=request.page_context.model_dump() if request.page_context else None
        ),
        media_type="text/event-stream"
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)