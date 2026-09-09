"""
系统配置文件
集中管理所有参数，便于调优和部署
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv(Path(__file__).parent.parent / ".env")

# 配置 HuggingFace 国内镜像（解决下载超时问题）
os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")

# 项目根目录
BASE_DIR = Path(__file__).parent.parent

# 数据目录
DATA_DIR = BASE_DIR / "data"
PAPERS_DIR = DATA_DIR / "papers"
CHROMA_DIR = DATA_DIR / "chroma_db"

# 确保目录存在
PAPERS_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_DIR.mkdir(parents=True, exist_ok=True)

# LLM 配置
LLM_CONFIG = {
    "provider": os.getenv("LLM_PROVIDER", "openai"),
    "api_key": os.getenv("OPENAI_API_KEY", ""),
    "base_url": os.getenv("LLM_BASE_URL", "https://api.openai.com/v1"),
    "model_name": os.getenv("LLM_MODEL", "gpt-4o-mini"),
    "temperature": 0.1,
    "max_tokens": 2048,
}

# Embedding 配置
EMBEDDING_CONFIG = {
    "model_name": os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-zh-v1.5"),
    "dimension": 512,
    "batch_size": 32,
    "device": os.getenv("EMBEDDING_DEVICE", "cpu"),
}

# 重排序配置
RERANKER_CONFIG = {
    "enabled": True,
    "model_name": os.getenv("RERANKER_MODEL", "BAAI/bge-reranker-base"),
    "top_n": 10,
    "device": os.getenv("RERANKER_DEVICE", "cpu"),
}

# 分块配置（参考 ScholarRAG 的学术感知分块）
CHUNKING_CONFIG = {
    "chunk_size": 512,        # 目标 chunk 大小（字符数）
    "chunk_overlap": 100,     # 重叠大小
    "min_chunk_size": 100,    # 最小 chunk 大小
    "sentence_boundary": True,  # 按句子边界切分
}

# 检索配置
RETRIEVAL_CONFIG = {
    "top_k": 20,              # 初始检索数量
    "final_k": 5,             # 最终返回数量
    "hybrid_weights": {       # 混合检索权重
        "dense": 0.6,
        "bm25": 0.4,
    },
    "rrf_k": 60,              # RRF 融合常数
}

# 学术缩写保护列表（分块时不被错误切分）
ACADEMIC_ABBREVIATIONS = [
    "i.e.", "e.g.", "et al.", "Fig.", "Figs.", "Eq.", "Eqs.",
    "Tab.", "Tabs.", "Sec.", "Secs.", "Ref.", "Refs.",
    "vs.", "etc.", "cf.", "op. cit.", "ibid.",
    "Dr.", "Prof.", "Mr.", "Mrs.", "Ms.",
    "approx.", "inc.", "ltd.", "co.",
    "No.", "Vol.", "pp.", "p.",
]

# 学术查询同义词（用于查询扩展）
ACADEMIC_SYNONYMS = {
    "方法": ["method", "approach", "technique", "framework", "methodology"],
    "实验": ["experiment", "experimental", "evaluation", "empirical"],
    "结果": ["result", "finding", "outcome", "performance"],
    "模型": ["model", "architecture", "network", "framework"],
    "数据集": ["dataset", "data set", "benchmark", "corpus"],
    "准确率": ["accuracy", "precision", "performance", "F1"],
    "对比": ["comparison", "compare", "versus", "vs", "baseline"],
    "创新": ["novel", "innovation", "contribution", "propose"],
    "相关工作": ["related work", "previous work", "literature", "background"],
    "结论": ["conclusion", "summary", "finding", "discussion"],
}
