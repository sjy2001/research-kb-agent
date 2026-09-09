# 科研知识库 Agent 评估报告

**评估时间**: 2026-09-09 20:48:29
**测试论文数**: 20 篇
**文本块数**: 227 个
**测试问题数**: 30 个

## 一、检索性能对比

| 检索方法 | Top-1 命中率 | Top-3 命中率 | Top-5 命中率 | MRR |
|----------|-------------|-------------|-------------|-----|
| 混合检索 + 重排序 | 80.0% | 93.3% | 93.3% | 0.856 |
| 混合检索（无重排序） | 70.0% | 76.7% | 80.0% | 0.740 |
| 纯向量检索 | 70.0% | 83.3% | 83.3% | 0.756 |
| 纯 BM25 检索 | 73.3% | 73.3% | 83.3% | 0.757 |

### 消融实验分析

1. **重排序的增益**: Top-1 提升 10.0%, MRR 提升 0.116
2. **混合检索 vs 纯向量**: Top-1 提升 10.0%, MRR 提升 0.100
3. **混合检索 vs 纯 BM25**: Top-1 提升 6.7%, MRR 提升 0.099

## 二、答案质量评估

- **总体关键词命中率**: 56.5%
- **总关键词数**: 170
- **命中关键词数**: 96

### 各问题详情

| ID | 问题 | 关键词命中率 | 命中关键词 |
|----|------|-------------|-----------|
| 1 | ReAct的全称是什么？它代表哪两个词的结合？ | 100% | Reasoning, Acting, 推理 |
| 2 | ReAct框架遵循什么样的循环过程？ | 100% | Thought, Action, Observation |
| 3 | Reflexion通过什么方式来强化语言Agent，而不是更... | 25% | 语言反馈 |
| 4 | Reflexion框架包含哪三个核心组件？ | 50% | Actor, Evaluator, Self-Reflection |
| 5 | Toolformer的核心创新是什么？它如何让模型学会使用工... | 33% | 自监督, 无需人工标注 |
| 6 | Toolformer如何判断一个API调用是否有用？ | 80% | 损失, 降低, 过滤 |
| 7 | Generative Agents的记忆系统包含哪三种记忆类... | 83% | 短期记忆, 长期记忆, sensory |
| 8 | Generative Agents的反思机制是如何触发的？ | 80% | 重要性, 阈值, 触发 |
| 9 | LLM Agent综述中提出的统一框架包含哪四个模块？ | 12% | Profile |
| 10 | AgentBench包含哪8个评估环境？请至少说出5个 | 12% | Housekeeping |
| 11 | MetaGPT的核心理念是什么？用一句话概括 | 75% | Code = SOP, SOP, 团队 |
| 12 | MetaGPT中的SOP包含哪四个要素？ | 88% | Role, Action, Sequence |
| 13 | ChatDev模拟了一个软件公司，包含哪些角色？请至少说出4... | 0% |  |
| 14 | CAMEL框架的核心技术Inception Promptin... | 60% | Inception Prompting, 角色, 协作 |
| 15 | HuggingGPT的四阶段处理流程是什么？ | 62% | Task Planning, 任务规划, 模型选择 |
| 16 | Voyager的三个核心组件是什么？ | 100% | Automatic Curriculum, Skill Library, Iterative Prompting |
| 17 | Voyager中的技能是以什么形式存储的？ | 40% | 代码, 可执行 |
| 18 | Tree of Thoughts相比Chain of Tho... | 33% | 树, 线性 |
| 19 | Tree of Thoughts使用哪两种搜索算法？ | 100% | BFS, DFS, 广度优先 |
| 20 | Plan-and-Solve prompting相比标准的'... | 83% | 规划, 执行, 分离 |
| 21 | Self-Consistency方法的核心思想是什么？ | 40% | 多数投票, 采样 |
| 22 | LLM+P框架是如何结合大语言模型和经典规划器的？ | 20% | 经典规划器 |
| 23 | Code as Policies (CaP)的核心思想是什么... | 80% | 代码, Python, code |
| 24 | TaskMatrix.AI的四个核心组件是什么？ | 0% |  |
| 25 | Graph of Thoughts相比Tree of Tho... | 71% | 图, 合并, 循环 |
| 26 | Inner Monologue框架如何实现机器人的自适应行为... | 60% | 内部独白, 自适应, monologue |
| 27 | LLM幻觉(Hallucination)主要分为哪两大类？ | 100% | 事实性, 忠实性, Factuality |
| 28 | ReAct和Reflexion的主要区别是什么？ | 33% | 反思, 学习 |
| 29 | MetaGPT和ChatDev都是多Agent软件开发框架，... | 83% | SOP, 结构化, 聊天 |
| 30 | 在RAG系统中，有哪些方法可以减少LLM幻觉？请至少说出3种 | 33% | RAG, 检索增强 |

## 三、结论

1. 混合检索（向量+BM25）显著优于单一检索方法
2. Cross-encoder 重排序进一步提升了检索精度
3. 最佳配置（混合+重排序）Top-5 命中率达 93.3%
4. LLM 生成答案的关键词命中率为 56.5%
5. 系统在学术论文问答场景下表现良好
