"""
向量数据库模块
使用 ChromaDB 作为向量存储，支持持久化和增量索引
"""
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings

from .config import CHROMA_DIR
from .chunker import TextChunk


class VectorStore:
    """
    ChromaDB 向量存储封装
    - 持久化存储
    - 增量添加
    - 元数据过滤
    """

    def __init__(self, collection_name: str = "research_papers",
                 persist_dir: str = None):
        self.persist_dir = str(persist_dir or CHROMA_DIR)
        self.collection_name = collection_name

        # 初始化 ChromaDB 客户端
        self.client = chromadb.PersistentClient(
            path=self.persist_dir,
            settings=Settings(anonymized_telemetry=False)
        )

        # 获取或创建集合
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def add_chunks(self, chunks: List[TextChunk],
                   embeddings: List[List[float]]):
        """
        批量添加文本块和向量

        Args:
            chunks: 文本块列表
            embeddings: 对应的向量列表
        """
        if not chunks:
            return

        ids = [chunk.chunk_id for chunk in chunks]
        documents = [chunk.text for chunk in chunks]
        metadatas = [self._chunk_to_metadata(chunk) for chunk in chunks]

        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )

    def _chunk_to_metadata(self, chunk: TextChunk) -> Dict[str, Any]:
        """将文本块转换为 ChromaDB 元数据格式"""
        meta = {
            "paper_id": chunk.paper_id,
            "paper_title": chunk.paper_title,
            "page_num": chunk.page_num,
            "section": chunk.section,
            "chunk_index": chunk.chunk_index,
        }
        # 额外元数据（标量类型才能存入 ChromaDB）
        if chunk.metadata.get("year"):
            meta["year"] = chunk.metadata["year"]
        if chunk.metadata.get("file_path"):
            meta["file_path"] = chunk.metadata["file_path"]
        return meta

    def search(self, query_embedding: List[float],
               top_k: int = 20,
               filter: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        向量检索

        Args:
            query_embedding: 查询向量
            top_k: 返回数量
            filter: 元数据过滤条件

        Returns:
            检索结果列表，包含文档、元数据、距离
        """
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filter,
        )

        formatted_results = []
        if results["ids"] and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                formatted_results.append({
                    "id": doc_id,
                    "text": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i],
                    "score": 1 - results["distances"][0][i],  # 相似度
                })

        return formatted_results

    def get_all_papers(self) -> List[Dict[str, Any]]:
        """获取所有已索引的论文列表"""
        results = self.collection.get(
            include=["metadatas"]
        )

        papers = {}
        if results["metadatas"]:
            for meta in results["metadatas"]:
                if meta and meta.get("paper_id"):
                    pid = meta["paper_id"]
                    if pid not in papers:
                        papers[pid] = {
                            "paper_id": pid,
                            "title": meta.get("paper_title", "Unknown"),
                            "year": meta.get("year"),
                        }

        return list(papers.values())

    def get_stats(self) -> Dict[str, Any]:
        """获取数据库统计信息"""
        count = self.collection.count()
        papers = self.get_all_papers()
        return {
            "total_chunks": count,
            "total_papers": len(papers),
            "papers": papers,
        }

    def delete_paper(self, paper_id: str):
        """删除指定论文的所有块"""
        self.collection.delete(
            where={"paper_id": paper_id}
        )

    def clear(self):
        """清空集合"""
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
