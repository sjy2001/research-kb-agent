"""
科研知识库 Agent 核心模块
基于 LangChain + LangGraph 实现：
- 文档索引管道
- 多轮对话 Agent
- 工具调用（检索、论文信息查询）
- 来源引用
"""
from typing import List, Dict, Any, Optional, TypedDict
from pathlib import Path
import json

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

from .config import LLM_CONFIG, PAPERS_DIR
from .pdf_parser import parse_pdf_file, PaperMetadata
from .chunker import chunk_paper, TextChunk
from .embedder import TextEmbedder
from .vector_store import VectorStore
from .retriever import HybridRetriever, BM25Retriever, Reranker
from .query_expander import QueryExpander
from .query_rewriter import AcademicQueryRewriter, get_rewriter
from .document_parser import parse_document, get_supported_extensions


# ============ 提示词模板 ============

SYSTEM_PROMPT = """你是一个科研知识库智能助手，专门帮助研究人员快速查找和理解学术论文。

你的职责：
1. 基于检索到的论文内容回答用户问题
2. 所有回答必须引用来源，标注[论文标题, 页码]
3. 如果检索结果不足以回答问题，明确告知用户，不要编造
4. 对于学术问题，保持严谨、客观的语气
5. 可以建议相关的论文或研究方向

回答格式：
- 先给出简洁的答案
- 然后列出引用来源
- 如果有多个相关论文，可以做对比分析

注意：你只能使用检索到的信息，不要使用你的预训练知识回答专业问题。
"""


# ============ Agent 状态定义 ============

class AgentState(TypedDict):
    """Agent 状态"""
    messages: List[Dict[str, str]]
    query: str
    retrieved_docs: List[Dict[str, Any]]
    answer: str
    sources: List[Dict[str, Any]]


# ============ 科研知识库 Agent ============

class ResearchKnowledgeBaseAgent:
    """
    科研知识库智能问答 Agent
    - 文档索引管理
    - 混合检索问答
    - 多轮对话
    - 来源引用
    """

    def __init__(self):
        # 初始化组件
        self.embedder = TextEmbedder()
        self.vector_store = VectorStore()
        self.bm25_retriever = BM25Retriever()
        self.reranker = Reranker()
        self.retriever = HybridRetriever(
            self.vector_store,
            self.embedder,
            self.bm25_retriever,
            self.reranker
        )
        self.query_expander = QueryExpander()
        self.query_rewriter = get_rewriter()

        # 初始化 LLM
        self.llm = ChatOpenAI(
            model=LLM_CONFIG["model_name"],
            api_key=LLM_CONFIG["api_key"],
            base_url=LLM_CONFIG["base_url"],
            temperature=LLM_CONFIG["temperature"],
            max_tokens=LLM_CONFIG["max_tokens"],
        )

        # 内存中保存所有 chunk（用于 BM25）
        self._all_chunks: List[TextChunk] = []
        self._load_existing_chunks()

    def _load_existing_chunks(self):
        """从向量库加载已有 chunk（用于 BM25 索引）"""
        # 注意：完整实现需要从 ChromaDB 恢复所有 chunk
        # 简化版：启动时不加载，新添加的文档会加入
        pass

    # ============ 文档索引 ============

    def index_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """
        索引单个 PDF 文件

        Args:
            pdf_path: PDF 文件路径

        Returns:
            索引结果统计
        """
        # 1. 解析 PDF
        metadata, pages = parse_pdf_file(pdf_path)

        # 2. 分块
        chunks = chunk_paper(pages, metadata)

        if not chunks:
            return {"success": False, "error": "No text extracted from PDF"}

        # 3. 向量化
        texts = [chunk.text for chunk in chunks]
        embeddings = self.embedder.embed(texts)

        # 4. 存入向量库
        self.vector_store.add_chunks(chunks, embeddings)

        # 5. 更新 BM25 索引
        self._all_chunks.extend(chunks)
        self.bm25_retriever.build_index(self._all_chunks)

        return {
            "success": True,
            "paper_id": metadata.paper_id,
            "title": metadata.title,
            "authors": metadata.authors,
            "year": metadata.year,
            "total_pages": metadata.total_pages,
            "total_chunks": len(chunks),
        }

    def index_file(self, file_path: str) -> Dict[str, Any]:
        """
        索引单个文件（支持 PDF、TXT、DOCX）

        Args:
            file_path: 文件路径

        Returns:
            索引结果统计
        """
        try:
            # 1. 统一解析文档
            doc_info = parse_document(file_path)

            # 2. 分块
            chunks = chunk_paper(doc_info.pages, doc_info.metadata)

            if not chunks:
                return {"success": False, "error": "No text extracted from file", "file": file_path}

            # 3. 向量化
            texts = [chunk.text for chunk in chunks]
            embeddings = self.embedder.embed(texts)

            # 4. 存入向量库
            self.vector_store.add_chunks(chunks, embeddings)

            # 5. 更新 BM25 索引
            self._all_chunks.extend(chunks)
            self.bm25_retriever.build_index(self._all_chunks)

            return {
                "success": True,
                "paper_id": doc_info.metadata.paper_id,
                "title": doc_info.metadata.title,
                "authors": doc_info.metadata.authors,
                "year": doc_info.metadata.year,
                "total_pages": doc_info.metadata.total_pages,
                "total_chunks": len(chunks),
                "file_type": Path(file_path).suffix.lower(),
            }
        except Exception as e:
            return {
                "success": False,
                "file": file_path,
                "error": str(e),
            }

    def index_files(self, file_paths: List[str]) -> List[Dict[str, Any]]:
        """
        批量索引多个文件

        Args:
            file_paths: 文件路径列表

        Returns:
            每个文件的索引结果
        """
        results = []
        for file_path in file_paths:
            result = self.index_file(file_path)
            results.append(result)
        return results

    def index_directory(self, directory: str = None) -> List[Dict[str, Any]]:
        """
        批量索引目录下的所有 PDF

        Args:
            directory: 目录路径，默认使用 data/papers

        Returns:
            每个文件的索引结果
        """
        directory = Path(directory or PAPERS_DIR)
        results = []

        pdf_files = list(directory.glob("*.pdf")) + list(directory.glob("*.PDF"))
        for pdf_file in pdf_files:
            try:
                result = self.index_pdf(str(pdf_file))
                results.append(result)
            except Exception as e:
                results.append({
                    "success": False,
                    "file": str(pdf_file),
                    "error": str(e),
                })

        return results

    # ============ 问答 ============

    def query(self, question: str,
              chat_history: List[Dict] = None,
              return_retrieval_details: bool = True) -> Dict[str, Any]:
        """
        回答用户问题

        Args:
            question: 用户问题
            chat_history: 对话历史
            return_retrieval_details: 是否返回检索过程详情

        Returns:
            回答结果，包含答案和来源
        """
        # 1. 智能查询改写（自研创新点）
        rewrite_result = self.query_rewriter.rewrite(question)

        # 2. 查询扩展（用改写后的查询进行扩展）
        expanded_queries = []
        for rewritten_q in rewrite_result.rewritten_queries:
            expanded = self.query_expander.expand(rewritten_q)
            expanded_queries.extend(expanded)
        # 保留原始问题的扩展
        expanded_queries.extend(self.query_expander.expand(question))
        # 去重
        seen_q = set()
        unique_expanded = []
        for q in expanded_queries:
            if q not in seen_q:
                seen_q.add(q)
                unique_expanded.append(q)
        expanded_queries = unique_expanded[:4]  # 最多用4个查询

        # 3. 混合检索
        all_docs = []
        retrieval_details = {
            "expanded_queries": expanded_queries,
            "rewrite_info": {
                "original_query": rewrite_result.original_query,
                "question_type": rewrite_result.question_type,
                "question_type_desc": rewrite_result.question_type_desc,
                "rewritten_queries": rewrite_result.rewritten_queries,
                "extracted_keywords": rewrite_result.extracted_keywords,
                "rewrite_reason": rewrite_result.rewrite_reason,
                "confidence": rewrite_result.confidence,
            },
            "vector_results": [],
            "bm25_results": [],
            "fused_results": [],
            "reranked_results": [],
        }

        for q in expanded_queries[:2]:  # 最多用2个查询
            # 分别获取向量和BM25结果（用于可视化）
            query_emb = self.embedder.embed_single(q)
            vector_docs = self.vector_store.search(query_emb, top_k=10)
            bm25_docs = self.bm25_retriever.search(q, top_k=10)

            # 混合检索（带重排序）
            docs = self.retriever.retrieve(q, top_k=5)
            all_docs.extend(docs)

            # 记录第一次查询的详情用于展示
            if not retrieval_details["vector_results"]:
                retrieval_details["vector_results"] = vector_docs[:5]
                retrieval_details["bm25_results"] = bm25_docs[:5]
                # RRF融合后的结果（无重排序）
                fused = self.retriever.retrieve(q, top_k=5, use_rerank=False)
                retrieval_details["fused_results"] = fused
                retrieval_details["reranked_results"] = docs

        # 去重
        seen_ids = set()
        unique_docs = []
        for doc in all_docs:
            if doc["id"] not in seen_ids:
                seen_ids.add(doc["id"])
                unique_docs.append(doc)

        # 3. 构建上下文
        context = self._build_context(unique_docs)

        # 4. 构建消息
        messages = [SystemMessage(content=SYSTEM_PROMPT)]

        # 添加对话历史
        if chat_history:
            for msg in chat_history[-6:]:  # 保留最近6轮
                if msg["role"] == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    messages.append(AIMessage(content=msg["content"]))

        # 添加当前问题和上下文
        user_prompt = f"""请基于以下检索到的论文内容回答问题。

检索到的论文内容：
{context}

用户问题：{question}

请回答问题，并在答案中标注引用来源。如果检索内容不足以回答，请说明。"""

        messages.append(HumanMessage(content=user_prompt))

        # 5. 调用 LLM
        response = self.llm.invoke(messages)

        # 6. 整理来源
        sources = self._format_sources(unique_docs)

        result = {
            "answer": response.content,
            "sources": sources,
            "retrieved_count": len(unique_docs),
            "expanded_queries": expanded_queries,
        }

        if return_retrieval_details:
            result["retrieval_details"] = retrieval_details

        return result

    def _build_context(self, docs: List[Dict[str, Any]]) -> str:
        """构建检索上下文"""
        context_parts = []
        for i, doc in enumerate(docs, 1):
            meta = doc.get("metadata", {})
            source_info = (
                f"[来源{i}] 论文: {meta.get('paper_title', 'Unknown')}, "
                f"页码: {meta.get('page_num', '?')}, "
                f"章节: {meta.get('section', 'Unknown')}"
            )
            context_parts.append(f"{source_info}\n{doc['text']}")

        return "\n\n---\n\n".join(context_parts)

    def _format_sources(self, docs: List[Dict[str, Any]]) -> List[Dict]:
        """格式化来源信息"""
        sources = []
        seen_papers = set()

        for doc in docs:
            meta = doc.get("metadata", {})
            paper_id = meta.get("paper_id", "")

            source = {
                "paper_title": meta.get("paper_title", "Unknown"),
                "page_num": meta.get("page_num", "?"),
                "section": meta.get("section", "Unknown"),
                "year": meta.get("year"),
                "relevance_score": round(doc.get("score", 0), 4),
            }

            # 同一篇论文只显示一次，但记录所有页码
            if paper_id not in seen_papers:
                seen_papers.add(paper_id)
                source["pages"] = [meta.get("page_num")]
                sources.append(source)
            else:
                for s in sources:
                    if s["paper_title"] == source["paper_title"]:
                        s["pages"].append(meta.get("page_num"))
                        break

        return sources

    # ============ 管理功能 ============

    def get_stats(self) -> Dict[str, Any]:
        """获取知识库统计"""
        return self.vector_store.get_stats()

    def list_papers(self) -> List[Dict[str, Any]]:
        """列出所有已索引论文"""
        return self.vector_store.get_all_papers()

    def clear_knowledge_base(self):
        """清空知识库"""
        self.vector_store.clear()
        self._all_chunks = []
        self.bm25_retriever = BM25Retriever()


# 全局单例
_agent_instance: Optional[ResearchKnowledgeBaseAgent] = None


def get_agent() -> ResearchKnowledgeBaseAgent:
    """获取 Agent 单例"""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = ResearchKnowledgeBaseAgent()
    return _agent_instance
