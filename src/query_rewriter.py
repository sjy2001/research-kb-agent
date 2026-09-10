"""
学术问题智能理解与查询改写模块
自研创新点：
- 问题类型识别（事实性/方法性/对比性/总结性/探索性）
- 学术查询改写（把口语化问题转成学术检索式）
- 关键词提取与权重分配
- 改写过程可解释、可视化
"""
import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field


@dataclass
class RewriteResult:
    """查询改写结果"""
    original_query: str
    question_type: str
    question_type_desc: str
    rewritten_queries: List[str]
    extracted_keywords: List[Dict[str, any]]
    rewrite_reason: str
    confidence: float


class AcademicQueryRewriter:
    """
    学术问题智能改写器
    1. 识别问题类型
    2. 提取核心关键词
    3. 生成学术化的检索查询
    """

    # 问题类型定义
    QUESTION_TYPES = {
        "factual": {
            "desc": "事实性问题",
            "patterns": [
                r"什么是|是什么|什么叫|定义|概念|含义",
                r"谁提出|哪一年|什么时候|时间",
                r"有多少|几个|数量|数据",
                r"全称|缩写|英文",
            ],
            "rewrite_templates": [
                "{keywords} 定义 概念",
                "{keywords} 提出 背景",
            ],
        },
        "method": {
            "desc": "方法性问题",
            "patterns": [
                r"怎么|如何|怎样|实现|做法",
                r"方法|算法|机制|原理|架构",
                r"流程|步骤|过程|框架",
                r"核心技术|创新点",
            ],
            "rewrite_templates": [
                "{keywords} 方法 原理 实现",
                "{keywords} 架构 流程 算法",
            ],
        },
        "comparison": {
            "desc": "对比性问题",
            "patterns": [
                r"区别|差异|不同|对比|比较",
                r"优势|劣势|优缺点|好处|坏处",
                r"哪个好|哪个更|相比|相较于",
                r"vs|VS| versus ",
            ],
            "rewrite_templates": [
                "{keywords} 对比 区别 优势",
                "{keywords} 比较 差异 性能",
            ],
        },
        "summary": {
            "desc": "总结性问题",
            "patterns": [
                r"总结|概括|综述|概述",
                r"贡献|主要工作|核心内容",
                r"结论|发现|结果",
                r"怎么样|如何评价|评价",
            ],
            "rewrite_templates": [
                "{keywords} 贡献 总结 结论",
                "{keywords} 主要工作 核心发现",
            ],
        },
        "exploratory": {
            "desc": "探索性问题",
            "patterns": [
                r"为什么|原因|因素",
                r"应用|场景|用途|用于",
                r"挑战|问题|局限|不足",
                r"未来|方向|趋势|展望",
            ],
            "rewrite_templates": [
                "{keywords} 应用 挑战 未来",
                "{keywords} 局限 改进 方向",
            ],
        },
    }

    # 学术停用词（不参与检索）
    STOP_WORDS = {
        "的", "了", "是", "在", "我", "你", "他", "她", "它",
        "这", "那", "有", "和", "与", "或", "及", "等",
        "什么", "怎么", "如何", "为什么", "哪些", "哪个",
        "可以", "能够", "应该", "需要", "请问", "一下",
        "the", "a", "an", "is", "are", "was", "were",
        "what", "how", "why", "which", "who", "when",
        "can", "could", "should", "would", "may", "might",
        "do", "does", "did", "to", "of", "in", "on",
        "for", "with", "and", "or", "not", "no",
    }

    # 学术领域关键词（提升权重）
    ACADEMIC_KEYWORDS = {
        "方法", "算法", "模型", "框架", "架构", "机制", "策略",
        "实验", "结果", "数据", "性能", "精度", "准确率",
        "提出", "实现", "设计", "优化", "改进", "创新",
        "对比", "分析", "评估", "验证", "证明",
        "method", "algorithm", "model", "framework",
        "architecture", "mechanism", "strategy",
        "experiment", "result", "performance", "accuracy",
        "propose", "implement", "design", "optimize",
        "comparison", "analysis", "evaluation",
    }

    def __init__(self):
        pass

    def rewrite(self, query: str) -> RewriteResult:
        """
        主入口：对用户问题进行智能改写

        Args:
            query: 用户原始问题

        Returns:
            RewriteResult 包含改写结果
        """
        # 1. 问题类型识别
        question_type, type_confidence = self._classify_question(query)

        # 2. 关键词提取
        keywords = self._extract_keywords(query)

        # 3. 生成改写后的查询
        rewritten_queries = self._generate_rewrites(query, question_type, keywords)

        # 4. 生成改写理由
        reason = self._generate_reason(query, question_type, keywords)

        type_desc = self.QUESTION_TYPES.get(question_type, {}).get("desc", "未知类型")

        return RewriteResult(
            original_query=query,
            question_type=question_type,
            question_type_desc=type_desc,
            rewritten_queries=rewritten_queries,
            extracted_keywords=keywords,
            rewrite_reason=reason,
            confidence=type_confidence,
        )

    def _classify_question(self, query: str) -> Tuple[str, float]:
        """
        识别问题类型

        Returns:
            (类型, 置信度)
        """
        query_lower = query.lower()
        scores = {}

        for qtype, config in self.QUESTION_TYPES.items():
            score = 0
            for pattern in config["patterns"]:
                if re.search(pattern, query_lower):
                    score += 1
            scores[qtype] = score

        if not scores or max(scores.values()) == 0:
            return "exploratory", 0.3

        best_type = max(scores, key=scores.get)
        total = sum(scores.values())
        confidence = scores[best_type] / total if total > 0 else 0.5

        return best_type, max(confidence, 0.4)

    def _extract_keywords(self, query: str) -> List[Dict[str, any]]:
        """
        提取核心关键词并分配权重

        Returns:
            [{"word": str, "weight": float, "is_academic": bool}]
        """
        # 简单分词：中英文混合处理
        # 英文按空格和标点，中文按2-4字滑动窗口（简化版）
        words = []

        # 提取英文单词和缩写
        english_words = re.findall(r'[a-zA-Z][a-zA-Z0-9+\-]*', query)
        for w in english_words:
            if w.lower() not in self.STOP_WORDS and len(w) > 1:
                words.append(w)

        # 提取中文词组（2-4字）
        chinese_segments = re.findall(r'[\u4e00-\u9fa5]+', query)
        for seg in chinese_segments:
            # 简单的中文关键词提取：匹配常见学术词汇
            for length in [4, 3, 2]:
                for i in range(len(seg) - length + 1):
                    word = seg[i:i+length]
                    if word not in self.STOP_WORDS and len(word) >= 2:
                        # 检查是否是有意义的词（简单启发式）
                        if not any(stop in word for stop in ["的", "了", "是", "在"]):
                            if word not in words:
                                words.append(word)

        # 分配权重
        weighted_keywords = []
        for word in words:
            weight = 1.0
            is_academic = False

            # 学术关键词提升权重
            if word in self.ACADEMIC_KEYWORDS or word.lower() in {k.lower() for k in self.ACADEMIC_KEYWORDS}:
                weight = 1.5
                is_academic = True

            # 英文专有名词（大写开头）提升权重
            if word[0].isupper() and len(word) > 2:
                weight = max(weight, 1.3)

            # 长词通常更具体
            if len(word) >= 4:
                weight = max(weight, 1.2)

            weighted_keywords.append({
                "word": word,
                "weight": round(weight, 2),
                "is_academic": is_academic,
            })

        # 按权重排序，取前10个
        weighted_keywords.sort(key=lambda x: x["weight"], reverse=True)
        return weighted_keywords[:10]

    def _generate_rewrites(self, query: str, question_type: str,
                           keywords: List[Dict]) -> List[str]:
        """
        生成改写后的学术查询
        """
        config = self.QUESTION_TYPES.get(question_type, self.QUESTION_TYPES["exploratory"])
        templates = config["rewrite_templates"]

        # 取权重最高的3-5个关键词
        top_keywords = [k["word"] for k in keywords[:5]]
        keyword_str = " ".join(top_keywords)

        rewritten = []
        for template in templates:
            rewritten_query = template.format(keywords=keyword_str)
            if rewritten_query not in rewritten:
                rewritten.append(rewritten_query)

        # 保留原始问题（去除口语化表达）
        cleaned = self._clean_query(query)
        if cleaned and cleaned not in rewritten:
            rewritten.append(cleaned)

        return rewritten[:3]  # 最多返回3个改写查询

    def _clean_query(self, query: str) -> str:
        """清理口语化表达，保留核心内容"""
        # 移除常见口语化前缀
        cleaned = re.sub(r'^(请问|我想|能不能|可以|帮我|告诉我|说说|讲讲)', '', query)
        cleaned = re.sub(r'[？?！!。.]$', '', cleaned)
        cleaned = cleaned.strip()
        return cleaned if len(cleaned) > 2 else query

    def _generate_reason(self, query: str, question_type: str,
                         keywords: List[Dict]) -> str:
        """生成改写理由（可解释性）"""
        type_desc = self.QUESTION_TYPES.get(question_type, {}).get("desc", "未知")

        top_keywords = [k["word"] for k in keywords[:3]]
        keyword_str = "、".join(top_keywords)

        reasons = {
            "factual": f"识别为{type_desc}，检索时侧重定义、背景等事实性内容",
            "method": f"识别为{type_desc}，检索时侧重方法、原理、实现等技术细节",
            "comparison": f"识别为{type_desc}，检索时侧重对比、差异、优势等分析内容",
            "summary": f"识别为{type_desc}，检索时侧重贡献、结论、核心工作等总结内容",
            "exploratory": f"识别为{type_desc}，检索时侧重应用、挑战、未来方向等探索内容",
        }

        reason = reasons.get(question_type, reasons["exploratory"])
        reason += f"；提取核心关键词：{keyword_str}"

        return reason


# 全局单例
_rewriter_instance: Optional[AcademicQueryRewriter] = None


def get_rewriter() -> AcademicQueryRewriter:
    """获取改写器单例"""
    global _rewriter_instance
    if _rewriter_instance is None:
        _rewriter_instance = AcademicQueryRewriter()
    return _rewriter_instance
