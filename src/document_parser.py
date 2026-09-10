"""
通用文档解析模块
支持 PDF、TXT、DOCX 格式的统一解析
"""
from pathlib import Path
from typing import Tuple, List
from dataclasses import dataclass

from .pdf_parser import parse_pdf_file, PaperMetadata, ParsedPage


@dataclass
class DocumentInfo:
    """解析后的文档信息"""
    metadata: PaperMetadata
    pages: List[ParsedPage]


def parse_document(file_path: str) -> DocumentInfo:
    """
    统一文档解析入口，根据文件扩展名自动选择解析方式

    Args:
        file_path: 文件路径

    Returns:
        DocumentInfo 包含元数据和页面内容

    Raises:
        ValueError: 不支持的文件格式
    """
    path = Path(file_path)
    ext = path.suffix.lower()

    if ext == ".pdf":
        return _parse_pdf(path)
    elif ext == ".txt":
        return _parse_txt(path)
    elif ext in [".docx", ".doc"]:
        return _parse_docx(path)
    else:
        raise ValueError(f"不支持的文件格式: {ext}，仅支持 PDF、TXT、DOCX")


def _parse_pdf(path: Path) -> DocumentInfo:
    """解析 PDF 文件"""
    metadata, pages = parse_pdf_file(str(path))
    return DocumentInfo(metadata=metadata, pages=pages)


def _parse_txt(path: Path) -> DocumentInfo:
    """解析 TXT 文件"""
    text = path.read_text(encoding="utf-8", errors="ignore")

    # 从文件名提取论文信息
    filename = path.stem
    parts = filename.split("_", 1)
    paper_id = parts[0] if len(parts) > 0 else filename
    title = parts[1].replace("_", " ") if len(parts) > 1 else filename

    # 按段落分割，模拟页面（每10段一页）
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    pages = []
    page_size = 10  # 每10段为一页

    for i in range(0, len(paragraphs), page_size):
        page_paragraphs = paragraphs[i:i + page_size]
        page_text = "\n\n".join(page_paragraphs)
        page_num = i // page_size + 1

        # 尝试识别章节标题
        section = "正文"
        for para in page_paragraphs:
            if para.isupper() and len(para) < 50:
                section = para
                break
            if any(kw in para.lower() for kw in ["abstract", "introduction", "method", "conclusion", "related work"]):
                section = para[:50]
                break

        pages.append(ParsedPage(
            page_num=page_num,
            text=page_text,
            section=section,
        ))

    metadata = PaperMetadata(
        paper_id=paper_id,
        title=title,
        authors=[],
        year=None,
        total_pages=len(pages),
    )

    return DocumentInfo(metadata=metadata, pages=pages)


def _parse_docx(path: Path) -> DocumentInfo:
    """解析 DOCX 文件"""
    try:
        import docx
    except ImportError:
        raise ImportError("请安装 python-docx: pip install python-docx")

    doc = docx.Document(str(path))

    # 提取所有段落文本
    paragraphs = []
    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            paragraphs.append(text)

    # 从文件名或文档属性提取标题
    filename = path.stem
    title = filename
    if doc.core_properties.title:
        title = doc.core_properties.title

    # 按段落分割，模拟页面（每10段一页）
    pages = []
    page_size = 10

    for i in range(0, len(paragraphs), page_size):
        page_paragraphs = paragraphs[i:i + page_size]
        page_text = "\n\n".join(page_paragraphs)
        page_num = i // page_size + 1

        # 识别章节标题（Word 中的 Heading 样式）
        section = "正文"
        for para in page_paragraphs:
            if len(para) < 50 and (para.isupper() or para.istitle()):
                section = para
                break

        pages.append(ParsedPage(
            page_num=page_num,
            text=page_text,
            section=section,
        ))

    metadata = PaperMetadata(
        paper_id=filename,
        title=title,
        authors=[doc.core_properties.author] if doc.core_properties.author else [],
        year=None,
        total_pages=len(pages),
    )

    return DocumentInfo(metadata=metadata, pages=pages)


def get_supported_extensions() -> List[str]:
    """返回支持的文件扩展名列表"""
    return [".pdf", ".txt", ".docx"]
