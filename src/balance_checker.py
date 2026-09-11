"""
API 余额与用量统计模块
- 记录每次调用的 token 使用量
- 计算已使用费用
- 支持查询 DeepSeek 账户余额（如接口可用）
"""
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


class BalanceChecker:
    """
    API 余额与用量统计
    """

    # DeepSeek 定价（元/百万 token），可通过环境变量覆盖
    DEFAULT_PRICING = {
        "input_per_million": 1.0,   # 输入 token 价格
        "output_per_million": 2.0,  # 输出 token 价格
    }

    def __init__(self, api_key: str = None, base_url: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.base_url = base_url or os.getenv("LLM_BASE_URL", "https://api.deepseek.com/v1")
        self.usage_file = Path(__file__).parent.parent / "data" / "usage_stats.json"
        self.usage_file.parent.mkdir(parents=True, exist_ok=True)
        self._usage = self._load_usage()

    def _load_usage(self) -> Dict[str, Any]:
        """加载本地用量统计"""
        if self.usage_file.exists():
            try:
                return json.loads(self.usage_file.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {
            "total_prompt_tokens": 0,
            "total_completion_tokens": 0,
            "total_calls": 0,
            "total_cost": 0.0,
            "history": [],
        }

    def _save_usage(self):
        """保存用量统计"""
        try:
            self.usage_file.write_text(
                json.dumps(self._usage, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
        except Exception as e:
            print(f"Save usage error: {e}")

    def record_usage(self, prompt_tokens: int, completion_tokens: int,
                     model: str = "deepseek-chat"):
        """
        记录一次 API 调用的用量

        Args:
            prompt_tokens: 输入 token 数
            completion_tokens: 输出 token 数
            model: 模型名称
        """
        pricing = self.DEFAULT_PRICING
        input_cost = prompt_tokens / 1_000_000 * pricing["input_per_million"]
        output_cost = completion_tokens / 1_000_000 * pricing["output_per_million"]
        cost = input_cost + output_cost

        self._usage["total_prompt_tokens"] += prompt_tokens
        self._usage["total_completion_tokens"] += completion_tokens
        self._usage["total_calls"] += 1
        self._usage["total_cost"] = round(self._usage["total_cost"] + cost, 6)

        # 记录最近100条历史
        self._usage["history"].append({
            "time": datetime.now().isoformat(),
            "model": model,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "cost": round(cost, 6),
        })
        if len(self._usage["history"]) > 100:
            self._usage["history"] = self._usage["history"][-100:]

        self._save_usage()

    def get_usage_stats(self) -> Dict[str, Any]:
        """获取用量统计"""
        return {
            "total_prompt_tokens": self._usage["total_prompt_tokens"],
            "total_completion_tokens": self._usage["total_completion_tokens"],
            "total_tokens": self._usage["total_prompt_tokens"] + self._usage["total_completion_tokens"],
            "total_calls": self._usage["total_calls"],
            "total_cost": round(self._usage["total_cost"], 4),
            "recent_calls": self._usage["history"][-5:],
        }

    def check_remote_balance(self) -> Optional[Dict[str, Any]]:
        """
        尝试查询远程账户余额

        Returns:
            余额信息，如果接口不可用则返回 None
        """
        try:
            import requests
            # DeepSeek 余额查询接口（如可用）
            balance_url = self.base_url.replace("/v1", "") + "/user/balance"
            headers = {"Authorization": f"Bearer {self.api_key}"}
            resp = requests.get(balance_url, headers=headers, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "balance": data.get("balance", data.get("available_balance", 0)),
                    "currency": "CNY",
                    "source": "remote_api",
                }
        except Exception as e:
            print(f"Remote balance check failed: {e}")

        return None

    def get_balance_info(self, initial_balance: float = None) -> Dict[str, Any]:
        """
        获取完整的余额信息

        Args:
            initial_balance: 用户设置的初始余额（元）

        Returns:
            余额信息
        """
        stats = self.get_usage_stats()
        result = {
            "used_cost": stats["total_cost"],
            "used_tokens": stats["total_tokens"],
            "total_calls": stats["total_calls"],
            "prompt_tokens": stats["total_prompt_tokens"],
            "completion_tokens": stats["total_completion_tokens"],
        }

        # 尝试远程查询
        remote = self.check_remote_balance()
        if remote:
            result["balance"] = remote["balance"]
            result["balance_source"] = "remote"
        elif initial_balance is not None:
            result["balance"] = round(initial_balance - stats["total_cost"], 4)
            result["balance_source"] = "estimated"
        else:
            result["balance"] = None
            result["balance_source"] = "unknown"

        return result


# 全局单例
_balance_instance: Optional[BalanceChecker] = None


def get_balance_checker() -> BalanceChecker:
    """获取余额检查器单例"""
    global _balance_instance
    if _balance_instance is None:
        _balance_instance = BalanceChecker()
    return _balance_instance
