"""
基础功能测试
验证核心模块能否正常导入和初始化
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def test_imports():
    """测试所有模块能否正常导入"""
    from src.config import (
        LLM_CONFIG, EMBEDDING_CONFIG, CHUNKING_CONFIG,
        RETRIEVAL_CONFIG, ACADEMIC_ABBREVIATIONS
    )
    assert LLM_CONFIG is not None
    assert EMBEDDING_CONFIG is not None
    assert CHUNKING_CONFIG is not None
    assert RETRIEVAL_CONFIG is not None
    assert len(ACADEMIC_ABBREVIATIONS) > 0
    print("✅ config 模块导入成功")


def test_pdf_parser():
    """测试 PDF 解析器"""
    from src.pdf_parser import AcademicPDFParser, PaperMetadata
    parser = AcademicPDFParser()
    assert parser is not None
    print("✅ pdf_parser 模块导入成功")


def test_chunker():
    """测试分块器"""
    from src.chunker import AcademicChunker, TextChunk
    chunker = AcademicChunker(chunk_size=100, chunk_overlap=20)

    # 测试学术缩写保护
    test_text = "As shown in Fig. 1, the method achieves state-of-the-art performance. See Eq. 2 for details. et al. proposed this approach."
    sentences = chunker._split_sentences(test_text)
    assert len(sentences) >= 2
    print(f"✅ chunker 模块导入成功，句子分割测试通过（{len(sentences)} 句）")


def test_query_expander():
    """测试查询扩展器"""
    from src.query_expander import QueryExpander
    expander = QueryExpander()
    expanded = expander.expand("这篇论文的方法是什么")
    assert len(expanded) >= 1
    print(f"✅ query_expander 模块导入成功，扩展结果: {expanded}")


def test_vector_store():
    """测试向量存储"""
    from src.vector_store import VectorStore
    store = VectorStore(collection_name="test_collection")
    assert store is not None
    store.clear()
    print("✅ vector_store 模块导入成功")


if __name__ == "__main__":
    print("=" * 50)
    print("运行基础功能测试...")
    print("=" * 50)

    test_imports()
    test_pdf_parser()
    test_chunker()
    test_query_expander()
    test_vector_store()

    print("=" * 50)
    print("🎉 所有基础测试通过！")
    print("=" * 50)
