"""
向量化模块
使用 sentence-transformers 进行文本向量化
支持批量处理和缓存
"""
from typing import List
import numpy as np

from .config import EMBEDDING_CONFIG


class TextEmbedder:
    """
    文本向量化器
    - 使用 sentence-transformers 模型
    - 支持批量处理
    - 支持 CPU/GPU
    """

    def __init__(self, model_name: str = None, device: str = None):
        self.model_name = model_name or EMBEDDING_CONFIG["model_name"]
        self.device = device or EMBEDDING_CONFIG["device"]
        self.batch_size = EMBEDDING_CONFIG["batch_size"]
        self._model = None

    @property
    def model(self):
        """懒加载模型"""
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(
                self.model_name,
                device=self.device
            )
        return self._model

    def embed(self, texts: List[str]) -> List[List[float]]:
        """
        对文本列表进行向量化

        Args:
            texts: 文本列表

        Returns:
            向量列表
        """
        if not texts:
            return []

        embeddings = self.model.encode(
            texts,
            batch_size=self.batch_size,
            show_progress_bar=False,
            normalize_embeddings=True,
        )

        return embeddings.tolist()

    def embed_single(self, text: str) -> List[float]:
        """对单条文本向量化"""
        return self.embed([text])[0]

    def get_dimension(self) -> int:
        """获取向量维度"""
        return EMBEDDING_CONFIG["dimension"]
