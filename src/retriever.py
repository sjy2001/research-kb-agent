"""
混合检索与重排序模块
参考 ScholarRAG 的实现：
- 稠密检索（向量相似度）
- 稀疏检索（BM25 关键词匹配）
- RRF（Reciprocal Rank Fusion）融合
- Cross-encoder 重排序
"""
from typing import List, Dict, Any, Optional
from rank_bm25 import BM25Okapi

from .config import RETRIEVAL_CONFIG, RERANKER_CONFIG
from .vector_store import VectorStore
from .embedder import TextEmbedder
from .chunker import TextChunk


class BM25Retriever:
    """BM25 关键词检索器"""

    def __init__(self):
        self.bm25 = None
        self.chunks: List[TextChunk] = []
        self._tokenized_corpus = []

    def build_index(self, chunks: List[TextChunk]):
        """构建 BM25 索引"""
        self.chunks = chunks
        self._tokenized_corpus = [
            self._tokenize(chunk.text) for chunk in chunks
        ]
        if self._tokenized_corpus:
            self.bm25 = BM25Okapi(self._tokenized_corpus)

    def _tokenize(self, text: str) -> List[str]:
        """简单分词（支持中英文）"""
        # 英文按空格和标点分词，中文按字符分词
        import re
        # 提取英文单词
        english_words = re.findall(r'[a-zA-Z]+', text.lower())
        # 提取中文字符
        chinese_chars = re.findall(r'[\u4e00-\u9fa5]', text)
        return english_words + chinese_chars

    def search(self, query: str, top_k: int = 20) -> List[Dict[str, Any]]:
        """BM25 检索"""
        if self.bm25 is None or not self.chunks:
            return []

        tokenized_query = self._tokenize(query)
        scores = self.bm25.get_scores(tokenized_query)

        # 按分数排序
        ranked_indices = sorted(
            range(len(scores)),
            key=lambda i: scores[i],
            reverse=True
        )[:top_k]

        results = []
        for rank, idx in enumerate(ranked_indices):
            if scores[idx] > 0:
                results.append({
                    "id": self.chunks[idx].chunk_id,
                    "text": self.chunks[idx].text,
                    "metadata": {
                        "paper_id": self.chunks[idx].paper_id,
                        "paper_title": self.chunks[idx].paper_title,
                        "page_num": self.chunks[idx].page_num,
                        "section": self.chunks[idx].section,
                    },
                    "score": float(scores[idx]),
                    "rank": rank,
                })

        return results


class Reranker:
    """Cross-encoder 重排序器"""

    def __init__(self, model_name: str = None, device: str = None):
        self.enabled = RERANKER_CONFIG["enabled"]
        self.model_name = model_name or RERANKER_CONFIG["model_name"]
        self.device = device or RERANKER_CONFIG["device"]
        self.top_n = RERANKER_CONFIG["top_n"]
        self._model = None

    @property
    def model(self):
        """懒加载模型"""
        if self._model is None and self.enabled:
            try:
                from sentence_transformers import CrossEncoder
                self._model = CrossEncoder(
                    self.model_name,
                    device=self.device
                )
            except Exception as e:
                print(f"Warning: Failed to load reranker: {e}")
                self.enabled = False
        return self._model

    def rerank(self, query: str,
               candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        对检索结果进行重排序

        Args:
            query: 查询文本
            candidates: 候选结果列表

        Returns:
            重排序后的结果
        """
        if not self.enabled or self.model is None or not candidates:
            return candidates[:self.top_n]

        # 准备输入对
        pairs = [(query, cand["text"]) for cand in candidates]

        # 计算相关性分数
        scores = self.model.predict(pairs)

        # 添加分数并排序
        for i, cand in enumerate(candidates):
            cand["rerank_score"] = float(scores[i])

        candidates.sort(key=lambda x: x.get("rerank_score", 0), reverse=True)

        return candidates[:self.top_n]


class HybridRetriever:
    """
    混合检索器
    结合稠密检索（向量）和稀疏检索（BM25），使用 RRF 融合
    """

    def __init__(self, vector_store: VectorStore,
                 embedder: TextEmbedder,
                 bm25_retriever: BM25Retriever = None,
                 reranker: Reranker = None):
        self.vector_store = vector_store
        self.embedder = embedder
        self.bm25_retriever = bm25_retriever or BM25Retriever()
        self.reranker = reranker or Reranker()
        self.config = RETRIEVAL_CONFIG

    def retrieve(self, query: str,
                 top_k: int = None,
                 use_rerank: bool = True) -> List[Dict[str, Any]]:
        """
        混合检索

        Args:
            query: 查询文本
            top_k: 最终返回数量
            use_rerank: 是否使用重排序

        Returns:
            检索结果列表
        """
        top_k = top_k or self.config["final_k"]
        initial_k = self.config["top_k"]

        # 1. 稠密检索
        query_embedding = self.embedder.embed_single(query)
        dense_results = self.vector_store.search(
            query_embedding, top_k=initial_k
        )

        # 2. BM25 检索
        bm25_results = self.bm25_retriever.search(query, top_k=initial_k)

        # 3. RRF 融合
        fused_results = self._rrf_fusion(dense_results, bm25_results)

        # 4. 重排序
        if use_rerank:
            fused_results = self.reranker.rerank(query, fused_results)

        return fused_results[:top_k]

    def _rrf_fusion(self, dense_results: List[Dict],
                    bm25_results: List[Dict]) -> List[Dict]:
        """
        Reciprocal Rank Fusion 融合
        score(d) = sum(1 / (k + rank_i(d)))
        """
        k = self.config["rrf_k"]
        scores = {}
        docs = {}

        # 稠密检索分数
        for rank, result in enumerate(dense_results):
            doc_id = result["id"]
            if doc_id not in scores:
                scores[doc_id] = 0
                docs[doc_id] = result
            scores[doc_id] += 1.0 / (k + rank + 1)

        # BM25 检索分数
        for rank, result in enumerate(bm25_results):
            doc_id = result["id"]
            if doc_id not in scores:
                scores[doc_id] = 0
                docs[doc_id] = result
            scores[doc_id] += 1.0 / (k + rank + 1)

        # 按融合分数排序
        sorted_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)

        fused = []
        for doc_id in sorted_ids:
            result = docs[doc_id].copy()
            result["fusion_score"] = scores[doc_id]
            fused.append(result)

        return fused
