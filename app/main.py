"""
FastAPI 后端服务
提供 REST API 接口：
- 文档上传与索引
- 智能问答
- 知识库管理
"""
from typing import List, Dict, Any, Optional
from pathlib import Path
import shutil

from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agent import get_agent
from src.config import PAPERS_DIR


app = FastAPI(
    title="科研知识库智能问答 Agent",
    description="基于 RAG 的学术论文智能问答系统",
    version="1.0.0",
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============ 请求/响应模型 ============

class QueryRequest(BaseModel):
    question: str
    chat_history: Optional[List[Dict[str, str]]] = None


class QueryResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    retrieved_count: int


class IndexResponse(BaseModel):
    success: bool
    paper_id: Optional[str] = None
    title: Optional[str] = None
    total_chunks: Optional[int] = None
    error: Optional[str] = None


# ============ API 路由 ============

@app.get("/")
async def root():
    """健康检查"""
    return {"status": "ok", "message": "科研知识库智能问答 Agent 运行中"}


@app.get("/stats")
async def get_stats():
    """获取知识库统计"""
    agent = get_agent()
    return agent.get_stats()


@app.get("/papers")
async def list_papers():
    """列出所有已索引论文"""
    agent = get_agent()
    return {"papers": agent.list_papers()}


@app.post("/upload", response_model=IndexResponse)
async def upload_pdf(file: UploadFile = File(...)):
    """上传并索引 PDF 文件"""
    if not file.filename.endswith(('.pdf', '.PDF')):
        return IndexResponse(success=False, error="只支持 PDF 文件")

    # 保存文件
    save_path = PAPERS_DIR / file.filename
    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # 索引
    agent = get_agent()
    try:
        result = agent.index_pdf(str(save_path))
        return IndexResponse(**result)
    except Exception as e:
        return IndexResponse(success=False, error=str(e))


@app.post("/index-directory")
async def index_directory(directory: str = Body(None, embed=True)):
    """批量索引目录下的 PDF"""
    agent = get_agent()
    results = agent.index_directory(directory)
    return {"results": results}


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """智能问答"""
    agent = get_agent()
    try:
        result = agent.query(
            question=request.question,
            chat_history=request.chat_history,
        )
        return QueryResponse(
            answer=result["answer"],
            sources=result["sources"],
            retrieved_count=result["retrieved_count"],
        )
    except Exception as e:
        raise HTTPQuery(status_code=500, detail=str(e))


@app.delete("/papers/{paper_id}")
async def delete_paper(paper_id: str):
    """删除指定论文"""
    agent = get_agent()
    agent.vector_store.delete_paper(paper_id)
    return {"success": True, "deleted": paper_id}


@app.post("/clear")
async def clear_knowledge_base():
    """清空知识库"""
    agent = get_agent()
    agent.clear_knowledge_base()
    return {"success": True, "message": "知识库已清空"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
