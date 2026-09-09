# 科研知识库智能问答 Agent

基于 RAG（检索增强生成）的学术论文智能问答系统，专为大学研究场景设计。

## 功能特性

### 核心功能
- 📄 **学术论文解析**：自动提取 PDF 文本、标题、作者、年份、摘要、关键词
- 🔍 **混合检索**：向量检索 + BM25 关键词检索，RRF 融合
- 🎯 **智能重排序**：Cross-encoder 重排序模型提升检索精度
- 💬 **多轮对话**：支持上下文追问，保持对话连贯性
- 📚 **来源引用**：每个答案标注论文标题、页码、章节
- 🔄 **查询扩展**：学术同义词扩展，提升检索召回率

### 学术特色
- 学术缩写保护（Fig.、Eq.、et al. 等不被错误切分）
- 句子边界感知分块
- 论文章节结构识别
- 元数据过滤检索

## 技术架构

```
用户提问
   ↓
查询扩展（学术同义词）
   ↓
混合检索 ──┬── 稠密检索（BGE Embedding + ChromaDB）
           ├── BM25 关键词检索
           └── RRF 融合
   ↓
Cross-encoder 重排序
   ↓
上下文构建
   ↓
LLM 生成答案（带引用来源）
```

## 技术栈

| 组件 | 技术 |
|------|------|
| Agent 框架 | LangChain + LangGraph |
| 向量数据库 | ChromaDB |
| Embedding | BGE-small-zh |
| 重排序 | BGE-reranker-base |
| PDF 解析 | PyMuPDF |
| 后端 | FastAPI |
| 前端 | Streamlit |
| 部署 | Docker |

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env，填入你的 API Key
```

### 3. 启动 Web 界面

```bash
streamlit run app/streamlit_app.py
```

### 4. 启动 API 服务（可选）

```bash
python -m app.main
# 或
uvicorn app.main:app --reload
```

## 使用方法

### 上传论文
1. 在侧边栏选择 PDF 文件
2. 点击"开始索引"
3. 等待解析和向量化完成

### 提问
- 在聊天框输入问题
- 系统自动检索相关论文内容
- 回答附带引用来源，可点击查看详情

### API 调用

```bash
# 上传论文
curl -X POST http://localhost:8000/upload \
  -F "file=@paper.pdf"

# 提问
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "这篇论文的核心方法是什么？"}'
```

## 项目结构

```
research-kb-agent/
├── src/
│   ├── config.py           # 配置文件
│   ├── pdf_parser.py       # PDF 解析与元数据提取
│   ├── chunker.py          # 学术感知分块
│   ├── embedder.py         # 文本向量化
│   ├── vector_store.py     # 向量数据库
│   ├── retriever.py        # 混合检索与重排序
│   ├── query_expander.py   # 查询扩展
│   └── agent.py            # Agent 核心逻辑
├── app/
│   ├── main.py             # FastAPI 后端
│   └── streamlit_app.py    # Streamlit 前端
├── data/
│   ├── papers/             # PDF 文件存放
│   └── chroma_db/          # 向量数据库
├── tests/                  # 测试
├── requirements.txt
├── Dockerfile
└── README.md
```

## 参考项目

- [ScholarRAG](https://github.com/Wh1esky/ScholarRAG/) - 多粒度 RAG 学术论文问答
- [Research Paper RAG System](https://github.com/nasirml/rag-chatbot-research-paper) - 学术论文 RAG 系统
- [LightRAG](https://github.com/HKUDS/LightRAG) - 轻量级 RAG 框架

## 许可证

MIT
