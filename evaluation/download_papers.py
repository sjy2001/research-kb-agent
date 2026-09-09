"""
直接从 arXiv 下载 20 篇经典 AI Agent 论文
"""
import os
import time
import ssl
import urllib.request
from pathlib import Path

SAVE_DIR = Path(__file__).parent.parent / "data" / "papers"
SAVE_DIR.mkdir(parents=True, exist_ok=True)

# 忽略 SSL 证书验证
ssl._create_default_https_context = ssl._create_unverified_context

# 20 篇经典 AI Agent / LLM 相关论文
PAPERS = [
    ("2210.03629", "ReAct-Synergizing Reasoning and Acting"),
    ("2303.11366", "Reflexion-Language Agents with Verbal Reinforcement"),
    ("2302.04761", "Toolformer-Language Models Can Teach Themselves Tools"),
    ("2304.03442", "Generative Agents-Interactive Simulacra"),
    ("2308.11432", "Survey on LLM based Autonomous Agents"),
    ("2308.03688", "AgentBench-Evaluating LLMs as Agents"),
    ("2308.00352", "MetaGPT-Meta Programming Multi-Agent"),
    ("2307.07924", "ChatDev-Communicative Agents Software Dev"),
    ("2303.17760", "CAMEL-Communicative Agents Mind Exploration"),
    ("2303.17580", "HuggingGPT-Solving AI Tasks with ChatGPT"),
    ("2305.16291", "Voyager-Open-Ended Embodied Agent LLM"),
    ("2305.10601", "Tree of Thoughts-Deliberate Problem Solving"),
    ("2305.04091", "Plan-and-Solve Prompting Improving Zero-Shot"),
    ("2203.11171", "Self-Consistency Improves Chain of Thought"),
    ("2304.11477", "LLM+P-Empowering LLMs with Optimal Planning"),
    ("2209.07753", "Code as Policies-Language Model Programs"),
    ("2303.16434", "TaskMatrix-AI Connecting Models with APIs"),
    ("2308.09687", "Graph of Thoughts-Solving Elaborate Problems"),
    ("2207.05608", "Inner Monologue-Embodied Reasoning Planning"),
    ("2401.03568", "A Survey on Hallucination in LLMs"),
]


def download_pdf(arxiv_id, title):
    """下载单篇论文"""
    url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
    filename = f"{arxiv_id}_{title}.pdf"
    filepath = SAVE_DIR / filename

    if filepath.exists() and filepath.stat().st_size > 10000:
        print(f"  ✓ 已存在")
        return True

    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        with urllib.request.urlopen(req, timeout=60) as response:
            data = response.read()

        if len(data) > 10000:
            with open(filepath, "wb") as f:
                f.write(data)
            print(f"  ✓ 成功 ({len(data)//1024} KB)")
            return True
        else:
            print(f"  ✗ 文件太小 ({len(data)} bytes)")
            return False
    except Exception as e:
        print(f"  ✗ 失败: {e}")
        return False


def main():
    print("=" * 60)
    print(f"从 arXiv 直接下载 {len(PAPERS)} 篇论文...")
    print("=" * 60)

    success = 0
    for i, (arxiv_id, title) in enumerate(PAPERS, 1):
        print(f"\n[{i}/{len(PAPERS)}] {arxiv_id} - {title[:45]}")
        if download_pdf(arxiv_id, title):
            success += 1
        time.sleep(2)

    print("\n" + "=" * 60)
    print(f"完成！成功 {success}/{len(PAPERS)} 篇")
    print(f"目录: {SAVE_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
