"""
查询扩展模块
参考 Research Paper RAG System 的实现：
- 学术同义词扩展
- 查询改写
- 多查询生成
"""
from typing import List
import re

from .config import ACADEMIC_SYNONYMS


class QueryExpander:
    """
    学术查询扩展器
    - 同义词替换
    - 中英双语扩展
    - 查询改写
    """

    def __init__(self):
        self.synonyms = ACADEMIC_SYNONYMS

    def expand(self, query: str) -> List[str]:
        """
        扩展查询，返回多个查询变体

        Args:
            query: 原始查询

        Returns:
            查询变体列表
        """
        expanded = [query]

        # 1. 同义词替换
        synonym_variant = self._replace_synonyms(query)
        if synonym_variant != query:
            expanded.append(synonym_variant)

        # 2. 提取关键词组合
        keywords = self._extract_keywords(query)
        if keywords and len(keywords) >= 2:
            keyword_query = " ".join(keywords)
            if keyword_query != query:
                expanded.append(keyword_query)

        # 去重
        seen = set()
        unique = []
        for q in expanded:
            q_lower = q.lower().strip()
            if q_lower not in seen and q_lower:
                seen.add(q_lower)
                unique.append(q)

        return unique

    def _replace_synonyms(self, query: str) -> str:
        """替换学术同义词"""
        result = query
        for term, synonyms in self.synonyms.items():
            # 如果查询中包含中文术语，添加英文同义词
            if term in query:
                for syn in synonyms[:2]:  # 只取前2个
                    if syn.lower() not in query.lower():
                        result += f" {syn}"
        return result

    def _extract_keywords(self, query: str) -> List[str]:
        """提取查询中的关键词"""
        # 移除停用词
        stopwords = {
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人',
            '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去',
            'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
            'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'could', 'should', 'may', 'might', 'can', 'shall',
            'what', 'which', 'who', 'whom', 'this', 'that', 'these',
            'those', 'and', 'but', 'if', 'or', 'because', 'as', 'until',
            'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between',
            'into', 'through', 'during', 'before', 'after', 'above', 'below',
            'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over',
        }

        # 英文单词
        english_words = re.findall(r'[a-zA-Z]+', query.lower())
        # 中文词（简单按2-4字切分）
        chinese_words = re.findall(r'[\u4e00-\u9fa5]{2,4}', query)

        keywords = []
        for w in english_words + chinese_words:
            if w not in stopwords and len(w) > 1:
                keywords.append(w)

        return keywords
