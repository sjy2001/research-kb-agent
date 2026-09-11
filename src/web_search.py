"""
联网搜索模块
当知识库中找不到答案时，自动联网搜索并返回结果和链接
"""
from typing import List, Dict, Any, Optional
import os


class WebSearcher:
    """
    联网搜索器
    使用 DuckDuckGo 搜索，无需 API Key
    """

    def __init__(self, max_results: int = 5):
        self.max_results = max_results
        self._ddgs = None

    def _get_ddgs(self):
        """懒加载 DDGS 实例"""
        if self._ddgs is None:
            from duckduckgo_search import DDGS
            self._ddgs = DDGS()
        return self._ddgs

    def search(self, query: str, max_results: int = None) -> List[Dict[str, Any]]:
        """
        联网搜索

        Args:
            query: 搜索关键词
            max_results: 返回结果数量

        Returns:
            搜索结果列表，每个包含 title、url、snippet
        """
        max_results = max_results or self.max_results
        results = []

        try:
            ddgs = self._get_ddgs()
            search_results = ddgs.text(
                query,
                max_results=max_results,
            )

            for r in search_results:
                results.append({
                    "title": r.get("title", ""),
                    "url": r.get("href", ""),
                    "snippet": r.get("body", ""),
                })

        except Exception as e:
            print(f"Web search error: {e}")
            # 搜索失败时返回空列表，不影响主流程

        return results

    def format_for_context(self, results: List[Dict[str, Any]]) -> str:
        """
        将搜索结果格式化为 LLM 上下文

        Args:
            results: 搜索结果列表

        Returns:
            格式化的文本
        """
        if not results:
            return ""

        parts = ["【联网搜索结果】"]
        for i, r in enumerate(results, 1):
            parts.append(
                f"[{i}] {r['title']}\n"
                f"链接: {r['url']}\n"
                f"摘要: {r['snippet']}"
            )

        return "\n\n".join(parts)


# 全局单例
_searcher_instance: Optional[WebSearcher] = None


def get_web_searcher() -> WebSearcher:
    """获取搜索器单例"""
    global _searcher_instance
    if _searcher_instance is None:
        _searcher_instance = WebSearcher()
    return _searcher_instance
