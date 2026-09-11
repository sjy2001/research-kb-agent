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
    st.subheader("📄 上传文档")
    uploaded_files = st.file_uploader(
        "选择 PDF / TXT / Word 文件（可多选）",
        type=["pdf", "txt", "docx"],
        accept_multiple_files=True,
        help="支持批量上传 PDF、TXT、DOCX 格式的学术文档"
    )

    if uploaded_files:
        if st.button("开始索引", type="primary"):
            with st.spinner(f"正在解析和索引 {len(uploaded_files)} 个文档..."):
                success_count = 0
                for uploaded_file in uploaded_files:
                    # 保存临时文件
                    temp_path = Path("data/papers") / uploaded_file.name
                    temp_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())

                    # 索引
                    result = st.session_state.agent.index_file(str(temp_path))
                    if result.get("success"):
                        success_count += 1
                        st.success(f"✅ {result['title']} ({result['total_chunks']} 块)")
                    else:
                        st.error(f"❌ {uploaded_file.name}: {result.get('error', '未知错误')}")

                if success_count > 0:
                    st.info(f"完成！成功索引 {success_count}/{len(uploaded_files)} 个文档")
                    st.rerun()

    st.markdown("---")

    # 知识库统计
    st.subheader("📊 知识库统计")
    if st.button("刷新统计"):
        stats = st.session_state.agent.get_stats()
        st.metric("已索引论文", stats["total_papers"])
        st.metric("文本块总数", stats["total_chunks"])

    # 显示已索引论文（支持单独删除）
    stats = st.session_state.agent.get_stats()
    if stats["papers"]:
        st.subheader("📋 已索引论文")
        for paper in stats["papers"]:
            year = f" ({paper['year']})" if paper.get('year') else ""
            col_title, col_del = st.columns([4, 1])
            with col_title:
                st.text(f"• {paper['title'][:45]}{year}")
            with col_del:
                if st.button("🗑️", key=f"del_{paper['paper_id']}", help="删除这篇论文"):
                    result = st.session_state.agent.remove_paper(paper['paper_id'])
                    if result.get("success"):
                        st.success(f"已删除 {result['removed_chunks']} 个文本块")
                        st.rerun()

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

            # 联网搜索结果展示
            if result.get("used_web_search") and result.get("web_results"):
                with st.expander("🌐 联网搜索结果", expanded=True):
                    st.info("知识库中未找到足够相关内容，已自动联网搜索补充")
                    for i, wr in enumerate(result["web_results"], 1):
                        st.markdown(f"**{i}. [{wr['title']}]({wr['url']})**")
                        st.caption(wr["snippet"][:200])
                        st.markdown("---")

            # 检索过程可视化
            if result.get("retrieval_details"):
                with st.expander("🔍 检索过程详情", expanded=False):
                    details = result["retrieval_details"]

                    # ===== 智能查询理解（自研创新点）=====
                    if details.get("rewrite_info"):
                        rw = details["rewrite_info"]
                        st.markdown("### 🧠 智能查询理解")

                        # 问题类型 + 置信度
                        col_type, col_conf = st.columns([2, 1])
                        with col_type:
                            st.info(f"**问题类型**：{rw['question_type_desc']}")
                        with col_conf:
                            st.metric("识别置信度", f"{rw['confidence']:.0%}")

                        # 提取的关键词
                        st.markdown("**🔑 提取关键词（按权重）**")
                        if rw.get("extracted_keywords"):
                            kw_cols = st.columns(len(rw["extracted_keywords"][:6]))
                            for i, kw in enumerate(rw["extracted_keywords"][:6]):
                                label = f"⭐ {kw['word']}" if kw["is_academic"] else kw["word"]
                                kw_cols[i].metric(label, f"×{kw['weight']}")

                        # 改写过程
                        st.markdown("**✏️ 查询改写过程**")
                        st.text(f"原始问题：{rw['original_query']}")
                        st.text(f"改写理由：{rw['rewrite_reason']}")

                        st.markdown("**改写后的检索查询：**")
                        for i, q in enumerate(rw["rewritten_queries"], 1):
                            st.code(f"查询{i}: {q}", language=None)

                        st.markdown("---")

                    # 查询扩展
                    if details.get("expanded_queries"):
                        st.markdown("**📝 查询扩展**")
                        cols = st.columns(min(len(details["expanded_queries"]), 4))
                        for i, q in enumerate(details["expanded_queries"][:4]):
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
