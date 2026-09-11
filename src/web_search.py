"""
联网搜索模块
当知识库中找不到答案时，自动联网搜索并返回结果和链接
使用百度搜索（国内可访问）
"""
from typing import List, Dict, Any, Optional
import re
import requests


class WebSearcher:
    """
    联网搜索器
    使用百度搜索，国内可访问，无需 API Key
    """

    def __init__(self, max_results: int = 5):
        self.max_results = max_results
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        }

    def search(self, query: str, max_results: int = None) -> List[Dict[str, Any]]:
        """
        联网搜索（百度）

        Args:
            query: 搜索关键词
            max_results: 返回结果数量

        Returns:
            搜索结果列表，每个包含 title、url、snippet
        """
        max_results = max_results or self.max_results
        results = []

        try:
            results = self._search_baidu(query, max_results)

            # 百度失败则尝试必应
            if not results:
                results = self._search_bing(query, max_results)

        except Exception as e:
            print(f"Web search error: {e}")

        return results[:max_results]

    def _search_baidu(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """百度搜索"""
        results = []
        url = f"https://www.baidu.com/s?wd={requests.utils.quote(query)}&rn={max_results * 2}"
        resp = requests.get(url, headers=self.headers, timeout=15)
        resp.encoding = "utf-8"

        if resp.status_code != 200:
            return results

        html = resp.text

        # 百度搜索结果：每个结果在 <div class="result c-container"> 中
        # 标题在 <h3><a href="...">标题</a></h3>
        # 摘要在 <span class="content-right_8Zs40"> 或 <div class="c-abstract"> 中

        # 提取所有结果块
        blocks = re.split(r'<div[^>]*class="[^"]*result[^"]*"[^>]*>', html)

        for block in blocks[1:max_results * 2 + 1]:
            # 提取标题和链接
            title_match = re.search(r'<h3[^>]*>.*?<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', block, re.DOTALL)
            if not title_match:
                continue

            link = title_match.group(1)
            title = re.sub(r'<[^>]+>', '', title_match.group(2)).strip()

            # 提取摘要（尝试多种class）
            snippet = ""
            # 方式1: c-abstract
            abstract_match = re.search(r'<span[^>]*class="[^"]*c-abstract[^"]*"[^>]*>(.*?)</span>', block, re.DOTALL)
            if abstract_match:
                snippet = re.sub(r'<[^>]+>', '', abstract_match.group(1)).strip()

            # 方式2: content-right
            if not snippet:
                content_match = re.search(r'<span[^>]*class="[^"]*content-right[^"]*"[^>]*>(.*?)</span>', block, re.DOTALL)
                if content_match:
                    snippet = re.sub(r'<[^>]+>', '', content_match.group(1)).strip()

            # 方式3: 任意 <p> 标签
            if not snippet:
                p_match = re.search(r'<p[^>]*>(.*?)</p>', block, re.DOTALL)
                if p_match:
                    snippet = re.sub(r'<[^>]+>', '', p_match.group(1)).strip()

            if title and link:
                results.append({
                    "title": title,
                    "url": link,
                    "snippet": snippet[:300] if snippet else "",
                })

            if len(results) >= max_results:
                break

        return results

    def _search_bing(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """必应搜索（备用）"""
        results = []
        url = f"https://www.bing.com/search?q={requests.utils.quote(query)}&count={max_results * 2}"
        resp = requests.get(url, headers=self.headers, timeout=15)
        resp.encoding = "utf-8"

        if resp.status_code != 200:
            return results

        html = resp.text

        # 必应结果在 <li class="b_algo"> 中
        blocks = re.split(r'<li[^>]*class="[^"]*b_algo[^"]*"[^>]*>', html)

        for block in blocks[1:max_results * 2 + 1]:
            # 提取标题和链接
            title_match = re.search(r'<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', block, re.DOTALL)
            if not title_match:
                continue

            link = title_match.group(1)
            title = re.sub(r'<[^>]+>', '', title_match.group(2)).strip()

            # 提取摘要
            snippet = ""
            p_match = re.search(r'<p[^>]*>(.*?)</p>', block, re.DOTALL)
            if p_match:
                snippet = re.sub(r'<[^>]+>', '', p_match.group(1)).strip()

            if title and link and 'bing.com' not in link:
                results.append({
                    "title": title,
                    "url": link,
                    "snippet": snippet[:300] if snippet else "",
                })

            if len(results) >= max_results:
                break

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
