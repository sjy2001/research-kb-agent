"""
学术感知文本分块模块
参考 ScholarRAG 的实现：
- 学术缩写保护（Fig.、Eq.、et al. 等不被错误切分）
- 句子边界感知切分
- 重叠机制
- 元数据保留
"""
import re
from dataclasses import dataclass, field
from typing import List, Dict, Any

from .config import CHUNKING_CONFIG, ACADEMIC_ABBREVIATIONS
from .pdf_parser import ParsedPage, PaperMetadata


@dataclass
class TextChunk:
    """文本块"""
    chunk_id: str
    text: str
    paper_id: str
    paper_title: str
    page_num: int
    section: str
    chunk_index: int
    metadata: Dict[str, Any] = field(default_factory=dict)


class AcademicChunker:
    """
    学术感知分块器
    核心改进：
    1. 保护学术缩写不被句子分割器错误切分
    2. 按句子边界切分，保证语义完整
    3. 重叠机制，减少上下文丢失
    4. 保留完整元数据（论文、页码、章节）
    """

    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        self.chunk_size = chunk_size or CHUNKING_CONFIG["chunk_size"]
        self.chunk_overlap = chunk_overlap or CHUNKING_CONFIG["chunk_overlap"]
        self.min_chunk_size = CHUNKING_CONFIG["min_chunk_size"]
        self.abbreviations = ACADEMIC_ABBREVIATIONS

    def chunk_pages(self, pages: List[ParsedPage],
                    metadata: PaperMetadata) -> List[TextChunk]:
        """
        将解析后的页面分块

        Args:
            pages: 解析后的页面列表
            metadata: 论文元数据

        Returns:
            文本块列表
        """
        chunks = []
        chunk_index = 0

        for page in pages:
            page_chunks = self._chunk_single_page(
                page.text, page.page_num, page.section, metadata
            )
            for chunk in page_chunks:
                chunk.chunk_index = chunk_index
                chunks.append(chunk)
                chunk_index += 1

        return chunks

    def _chunk_single_page(self, text: str, page_num: int,
                           section: str,
                           metadata: PaperMetadata) -> List[TextChunk]:
        """对单页文本进行分块"""
        if not text.strip():
            return []

        # 先分割成句子
        sentences = self._split_sentences(text)

        # 再按目标大小组合成 chunk
        chunks = []
        current_chunk = ""
        current_sentences = []

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            # 如果当前 chunk 加上这个句子超过目标大小，就保存当前 chunk
            if (len(current_chunk) + len(sentence) > self.chunk_size
                    and current_chunk):
                chunks.append(self._create_chunk(
                    current_chunk, page_num, section, metadata, len(chunks)
                ))
                # 保留重叠
                if current_sentences:
                    overlap_text = " ".join(
                        current_sentences[-2:]
                    )[-self.chunk_overlap:]
                    current_chunk = overlap_text + " " + sentence
                    current_sentences = [sentence]
                else:
                    current_chunk = sentence
                    current_sentences = [sentence]
            else:
                if current_chunk:
                    current_chunk += " " + sentence
                else:
                    current_chunk = sentence
                current_sentences.append(sentence)

        # 处理最后一个 chunk
        if current_chunk.strip() and len(current_chunk) >= self.min_chunk_size:
            chunks.append(self._create_chunk(
                current_chunk, page_num, section, metadata, len(chunks)
            ))

        return chunks

    def _split_sentences(self, text: str) -> List[str]:
        """
        学术感知句子分割
        保护 Fig.、Eq.、et al. 等缩写不被错误切分
        """
        # 先替换缩写中的句号为占位符
        protected_text = text
        for abbr in self.abbreviations:
            # 使用不区分大小写的替换
            pattern = re.escape(abbr)
            placeholder = abbr.replace('.', '∮')
            protected_text = re.sub(
                pattern, placeholder, protected_text, flags=re.IGNORECASE
            )

        # 按句子结束符分割
        sentences = re.split(r'(?<=[.!?。！？])\s+', protected_text)

        # 恢复缩写中的句号
        restored_sentences = []
        for s in sentences:
            restored = s.replace('∮', '.')
            restored_sentences.append(restored)

        return restored_sentences

    def _create_chunk(self, text: str, page_num: int, section: str,
                      metadata: PaperMetadata,
                      local_index: int) -> TextChunk:
        """创建文本块"""
        chunk_id = f"{metadata.paper_id}_p{page_num}_{local_index}"
        return TextChunk(
            chunk_id=chunk_id,
            text=text.strip(),
            paper_id=metadata.paper_id,
            paper_title=metadata.title,
            page_num=page_num,
            section=section,
            chunk_index=local_index,
            metadata={
                "authors": metadata.authors,
                "year": metadata.year,
                "keywords": metadata.keywords,
                "file_path": metadata.file_path,
            }
        )


def chunk_paper(pages: List[ParsedPage],
                metadata: PaperMetadata) -> List[TextChunk]:
    """便捷函数：对论文进行分块"""
    chunker = AcademicChunker()
    return chunker.chunk_pages(pages, metadata)
