"""FastAPI 应用入口。"""

import sys
from pathlib import Path

# 将 rag_agent 加入导入路径
sys.path.insert(0, str(Path(__file__).parent.parent / "rag_agent"))

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database import init_db
from backend.chat_api import router as chat_router
from backend.history_api import router as history_router

# 加载环境变量（从 rag_agent/.env）
env_path = Path(__file__).parent.parent / "rag_agent" / ".env"
load_dotenv(dotenv_path=env_path)

app = FastAPI(title="LangChain RAG Agent API")

# CORS 配置：允许前端开发服务器访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(history_router, prefix="/api")
app.include_router(chat_router, prefix="/api")


@app.on_event("startup")
async def startup():
    """应用启动时初始化数据库。"""
    init_db()


@app.get("/api/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8001, reload=True)
