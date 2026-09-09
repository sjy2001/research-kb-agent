"""
Streamlit 前端界面
提供交互式的科研知识库问答界面
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from src.agent import get_agent


# 页面配置
st.set_page_config(
    page_title="科研知识库智能问答 Agent",
    page_icon="📚",
    layout="wide",
)


# 初始化 session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "agent" not in st.session_state:
    st.session_state.agent = get_agent()


# ============ 侧边栏 ============

with st.sidebar:
    st.title("📚 科研知识库")
    st.markdown("---")

    # 上传文件
    st.subheader("📄 上传论文")
    uploaded_file = st.file_uploader(
        "选择 PDF 文件",
        type=["pdf"],
        help="上传学术论文 PDF 进行索引"
    )

    if uploaded_file:
        if st.button("开始索引", type="primary"):
            with st.spinner("正在解析和索引论文..."):
                # 保存临时文件
                temp_path = Path("data/papers") / uploaded_file.name
                temp_path.parent.mkdir(parents=True, exist_ok=True)
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                # 索引
                result = st.session_state.agent.index_pdf(str(temp_path))
                if result.get("success"):
                    st.success(f"✅ 索引完成: {result['title']}")
                    st.info(f"共 {result['total_chunks']} 个文本块")
                else:
                    st.error(f"❌ 索引失败: {result.get('error')}")

    st.markdown("---")

    # 知识库统计
    st.subheader("📊 知识库统计")
    if st.button("刷新统计"):
        stats = st.session_state.agent.get_stats()
        st.metric("已索引论文", stats["total_papers"])
        st.metric("文本块总数", stats["total_chunks"])

    # 显示已索引论文
    stats = st.session_state.agent.get_stats()
    if stats["papers"]:
        st.subheader("📋 已索引论文")
        for paper in stats["papers"][:10]:
            year = f" ({paper['year']})" if paper.get('year') else ""
            st.text(f"• {paper['title'][:50]}{year}")

    st.markdown("---")

    # 清空知识库
    if st.button("🗑️ 清空知识库", type="secondary"):
        st.session_state.agent.clear_knowledge_base()
        st.session_state.chat_history = []
        st.success("知识库已清空")
        st.rerun()


# ============ 主界面 ============

st.title("🔬 科研知识库智能问答")
st.markdown("上传学术论文，然后用自然语言提问，获取带引用来源的答案。")

# 聊天界面
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("sources"):
            with st.expander("📚 引用来源"):
                for i, source in enumerate(message["sources"], 1):
                    pages = ", ".join(map(str, source.get("pages", [])))
                    st.markdown(
                        f"**{i}. {source['paper_title']}**\n"
                        f"- 页码: {pages}\n"
                        f"- 章节: {source['section']}\n"
                        f"- 相关度: {source['relevance_score']}"
                    )

# 用户输入
if prompt := st.chat_input("输入你的问题，例如：这篇论文的核心方法是什么？"):
    # 添加用户消息
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 生成回答
    with st.chat_message("assistant"):
        with st.spinner("正在检索和生成答案..."):
            result = st.session_state.agent.query(
                question=prompt,
                chat_history=st.session_state.chat_history[:-1],
            )

            st.markdown(result["answer"])

            # 显示来源
            if result["sources"]:
                with st.expander("📚 引用来源"):
                    for i, source in enumerate(result["sources"], 1):
                        pages = ", ".join(map(str, source.get("pages", [])))
                        st.markdown(
                            f"**{i}. {source['paper_title']}**\n"
                            f"- 页码: {pages}\n"
                            f"- 章节: {source['section']}\n"
                            f"- 相关度: {source['relevance_score']}"
                        )

    # 添加助手消息
    st.session_state.chat_history.append({
        "role": "assistant",
        "content": result["answer"],
        "sources": result["sources"],
    })


# 底部信息
st.markdown("---")
st.caption(
    "基于 RAG 的科研知识库智能问答系统 | "
    "LangChain + ChromaDB + 混合检索 + 重排序"
)
