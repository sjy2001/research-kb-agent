"""
PDF 解析与学术元数据提取模块
参考 Research Paper RAG System 的实现，使用 PyMuPDF 进行文本提取，
并自动识别论文标题、作者、年份、摘要等元数据。
"""
import re
import hashlib
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple

try:
    import pymupdf as fitz  # 新版本
except ImportError:
    import fitz  # 旧版本兼容


@dataclass
class PaperMetadata:
    """论文元数据"""
    paper_id: str
    title: str
    authors: List[str] = field(default_factory=list)
    year: Optional[int] = None
    abstract: str = ""
    file_path: str = ""
    total_pages: int = 0
    keywords: List[str] = field(default_factory=list)


@dataclass
class ParsedPage:
    """解析后的单页内容"""
    page_num: int
    text: str
    section: str = ""


class AcademicPDFParser:
    """
    学术论文 PDF 解析器
    - 文本提取（PyMuPDF）
    - 页眉页脚清理
    - 元数据自动提取（标题、作者、年份、摘要）
    - 章节结构识别
    """

    def __init__(self):
        # 常见页眉页脚模式
        self.header_footer_patterns = [
            r'^\s*\d+\s*$',                              # 纯页码
            r'^\s*第\s*\d+\s*页.*$',                     # 中文页码
            r'^\s*Page\s*\d+.*$',                        # 英文页码
            r'^\s*arXiv:.*$',                            # arXiv 水印
            r'^\s*Preprint.*$',                          # 预印本标记
            r'^\s*Copyright.*$',                         # 版权声明
            r'^\s*©.*$',                                 # 版权符号
        ]

    def parse_pdf(self, pdf_path: str) -> Tuple[PaperMetadata, List[ParsedPage]]:
        """
        解析 PDF 文件，返回元数据和分页内容

        Args:
            pdf_path: PDF 文件路径

        Returns:
            (元数据, 分页内容列表)
        """
        pdf_path = str(pdf_path)
        doc = fitz.open(pdf_path)
        total_pages = len(doc)

        # 提取所有页面文本
        all_pages = []
        full_text = ""
        for page_num in range(total_pages):
            page = doc[page_num]
            text = page.get_text("text")
            text = self._clean_text(text)
            all_pages.append(ParsedPage(
                page_num=page_num + 1,
                text=text
            ))
            full_text += text + "\n"

        doc.close()

        # 提取元数据
        metadata = self._extract_metadata(pdf_path, full_text, total_pages)

        # 识别章节
        all_pages = self._identify_sections(all_pages)

        return metadata, all_pages

    def _clean_text(self, text: str) -> str:
        """清理文本，移除页眉页脚和多余空白"""
        lines = text.split('\n')
        cleaned_lines = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 检查是否是页眉页脚
            is_header_footer = False
            for pattern in self.header_footer_patterns:
                if re.match(pattern, line, re.IGNORECASE):
                    is_header_footer = True
                    break

            if not is_header_footer:
                cleaned_lines.append(line)

        return '\n'.join(cleaned_lines)

    def _extract_metadata(self, pdf_path: str, full_text: str,
                          total_pages: int) -> PaperMetadata:
        """从文本中提取论文元数据"""
        # 生成唯一 ID
        paper_id = hashlib.md5(
            Path(pdf_path).name.encode()
        ).hexdigest()[:12]

        # 提取标题（取前几行中最长的有意义行）
        title = self._extract_title(full_text)

        # 提取作者
        authors = self._extract_authors(full_text)

        # 提取年份
        year = self._extract_year(full_text)

        # 提取摘要
        abstract = self._extract_abstract(full_text)

        # 提取关键词
        keywords = self._extract_keywords(full_text)

        return PaperMetadata(
            paper_id=paper_id,
            title=title,
            authors=authors,
            year=year,
            abstract=abstract,
            file_path=pdf_path,
            total_pages=total_pages,
            keywords=keywords,
        )

    def _extract_title(self, text: str) -> str:
        """提取论文标题"""
        lines = [l.strip() for l in text.split('\n') if l.strip()]

        # 标题通常在前 10 行，且长度适中
        candidates = []
        for i, line in enumerate(lines[:15]):
            # 过滤明显不是标题的行
            if len(line) < 10 or len(line) > 300:
                continue
            if re.match(r'^\d+$', line):  # 纯数字
                continue
            if '@' in line:  # 邮箱
                continue
            if re.match(r'^(abstract|introduction|keywords)', line, re.I):
                break

            # 标题特征：首字母大写、不含太多特殊符号
            if re.match(r'^[A-Z\u4e00-\u9fa5]', line):
                score = len(line)
                # 包含更多实词的行得分更高
                words = line.split()
                if len(words) > 2:
                    score += 10
                candidates.append((score, line))

        if candidates:
            candidates.sort(reverse=True)
            return candidates[0][1]

        return lines[0] if lines else "Untitled"

    def _extract_authors(self, text: str) -> List[str]:
        """提取作者列表"""
        lines = [l.strip() for l in text.split('\n') if l.strip()]

        # 作者通常在标题之后，摘要之前
        for i, line in enumerate(lines[:20]):
            # 作者行特征：包含逗号分隔的名字，或有上标数字
            if (',' in line and len(line) < 200 and
                    not line.lower().startswith('abstract') and
                    '@' not in line):
                # 尝试分割作者
                authors = re.split(r'[,;]', line)
                authors = [a.strip() for a in authors
                           if a.strip() and len(a.strip()) > 1]
                # 过滤掉非作者内容
                authors = [a for a in authors
                           if not re.match(r'^\d+$', a)
                           and not a.lower() in ('and', 'et al')]
                if len(authors) >= 1:
                    return authors[:10]  # 最多取10个作者

        return []

    def _extract_year(self, text: str) -> Optional[int]:
        """提取发表年份"""
        # 查找 1900-2099 年间的年份
        matches = re.findall(r'\b(19|20)\d{2}\b', text[:2000])
        if matches:
            years = [int(m) for m in re.findall(r'\b(?:19|20)\d{2}\b', text[:2000])]
            # 取最常见的年份
            from collections import Counter
            year_counts = Counter(years)
            return year_counts.most_common(1)[0][0]
        return None

    def _extract_abstract(self, text: str) -> str:
        """提取摘要"""
        # 英文摘要
        match = re.search(
            r'Abstract\s*[:\-]?\s*(.+?)(?:\n\s*(?:1\.?\s*Introduction|Keywords|Index Terms))',
            text, re.DOTALL | re.IGNORECASE
        )
        if match:
            abstract = match.group(1).strip()
            return abstract[:2000]

        # 中文摘要
        match = re.search(
            r'摘\s*要\s*[:：]?\s*(.+?)(?:\n\s*(?:关键词|Key\s*words|1))',
            text, re.DOTALL
        )
        if match:
            abstract = match.group(1).strip()
            return abstract[:2000]

        return ""

    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 英文关键词
        match = re.search(
            r'(?:Keywords|Index Terms)\s*[:\-]?\s*(.+?)(?:\n|$)',
            text, re.IGNORECASE
        )
        if match:
            kw_text = match.group(1).strip()
            keywords = re.split(r'[,;]', kw_text)
            return [k.strip() for k in keywords if k.strip()][:10]

        # 中文关键词
        match = re.search(
            r'关键词\s*[:：]?\s*(.+?)(?:\n|$)',
            text
        )
        if match:
            kw_text = match.group(1).strip()
            keywords = re.split(r'[,;，；]', kw_text)
            return [k.strip() for k in keywords if k.strip()][:10]

        return []

    def _identify_sections(self, pages: List[ParsedPage]) -> List[ParsedPage]:
        """识别章节结构"""
        # 常见章节标题模式
        section_patterns = [
            r'^\s*(\d+\.?\d*\.?)\s*(Introduction|Related Work|Method|Methodology|'
            r'Approach|Experiments?|Results?|Evaluation|Discussion|Conclusion|'
            r'References|Background|Related Literature|Proposed|Framework|'
            r'Implementation|Analysis|Limitations|Future Work)\b',
            r'^\s*(引言|相关工作|方法|方法论|实验|结果|评估|讨论|结论|参考文献|'
            r'背景|提出|框架|实现|分析|局限性|未来工作)',
        ]

        current_section = "Front Matter"

        for page in pages:
            lines = page.text.split('\n')
            for line in lines:
                line = line.strip()
                for pattern in section_patterns:
                    match = re.match(pattern, line, re.IGNORECASE)
                    if match:
                        current_section = match.group(0).strip()
                        break
            page.section = current_section

        return pages


def parse_pdf_file(pdf_path: str) -> Tuple[PaperMetadata, List[ParsedPage]]:
    """便捷函数：解析单个 PDF 文件"""
    parser = AcademicPDFParser()
    return parser.parse_pdf(pdf_path)
