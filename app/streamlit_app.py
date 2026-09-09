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

            # 检索过程可视化
            if result.get("retrieval_details"):
                with st.expander("🔍 检索过程详情", expanded=False):
                    details = result["retrieval_details"]

                    # 查询扩展
                    if details.get("expanded_queries"):
                        st.markdown("**📝 查询扩展**")
                        cols = st.columns(len(details["expanded_queries"]))
                        for i, q in enumerate(details["expanded_queries"]):
                            cols[i].info(q)

                    st.markdown("---")

                    # 三列对比：向量、BM25、RRF融合
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.markdown("**🎯 向量检索 Top-5**")
                        for i, doc in enumerate(details.get("vector_results", [])[:5], 1):
                            score = doc.get("score", 0)
                            meta = doc.get("metadata", {})
                            with st.container(border=True):
                                st.markdown(f"**#{i}** | 相似度: `{score:.4f}`")
                                st.caption(f"📄 {meta.get('paper_title', '?')[:30]}")
                                st.text(doc.get("text", "")[:80] + "...")

                    with col2:
                        st.markdown("**🔑 BM25 检索 Top-5**")
                        for i, doc in enumerate(details.get("bm25_results", [])[:5], 1):
                            score = doc.get("score", 0)
                            meta = doc.get("metadata", {})
                            with st.container(border=True):
                                st.markdown(f"**#{i}** | BM25: `{score:.2f}`")
                                st.caption(f"📄 {meta.get('paper_title', '?')[:30]}")
                                st.text(doc.get("text", "")[:80] + "...")

                    with col3:
                        st.markdown("**🔀 RRF 融合 Top-5**")
                        for i, doc in enumerate(details.get("fused_results", [])[:5], 1):
                            score = doc.get("fusion_score", doc.get("score", 0))
                            meta = doc.get("metadata", {})
                            with st.container(border=True):
                                st.markdown(f"**#{i}** | 融合分: `{score:.4f}`")
                                st.caption(f"📄 {meta.get('paper_title', '?')[:30]}")
                                st.text(doc.get("text", "")[:80] + "...")

                    st.markdown("---")

                    # 重排序前后对比
                    st.markdown("**🎯 重排序效果对比**")
                    fused = details.get("fused_results", [])[:5]
                    reranked = details.get("reranked_results", [])[:5]

                    comparison_data = []
                    for i in range(max(len(fused), len(reranked))):
                        f_title = fused[i]["metadata"].get("paper_title", "?")[:25] if i < len(fused) else "-"
                        f_score = fused[i].get("fusion_score", 0) if i < len(fused) else 0
                        r_title = reranked[i]["metadata"].get("paper_title", "?")[:25] if i < len(reranked) else "-"
                        r_score = reranked[i].get("rerank_score", 0) if i < len(reranked) else 0
                        changed = "🔄" if f_title != r_title else "✓"
                        comparison_data.append({
                            "排名": f"#{i+1}",
                            "重排序前": f"{f_title} ({f_score:.3f})",
                            "重排序后": f"{r_title} ({r_score:.3f})",
                            "变化": changed,
                        })

                    st.dataframe(comparison_data, use_container_width=True, hide_index=True)

                    # 最终用于生成答案的片段
                    st.markdown("---")
                    st.markdown("**📖 最终用于生成答案的片段**")
                    for i, doc in enumerate(reranked[:3], 1):
                        meta = doc.get("metadata", {})
                        with st.container(border=True):
                            st.markdown(f"**片段 {i}** | {meta.get('paper_title', '?')}")
                            st.text(doc.get("text", "")[:200])

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
