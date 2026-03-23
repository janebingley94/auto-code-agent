from __future__ import annotations

from typing import Any, Dict

from openai import AsyncOpenAI

from tools.code_tools import extract_code_block


def _mock_fix(code: str) -> str:
    return code + "\n\n# Mock fix applied\n"


async def fixer_node(state: Dict[str, Any]) -> Dict[str, Any]:
    api_key = state.get("openai_api_key")
    language = state.get("language", "python")
    current_code = state.get("fixed_code") or state.get("generated_code", "")
    error = state.get("execution_error", "")

    if not api_key:
        fixed = _mock_fix(current_code)
        return {
            "fixed_code": fixed,
            "retry_count": state.get("retry_count", 0) + 1,
            "status": "fixing",
            "logs": [{"step": "Fixer", "message": "Mock fix applied", "error": error}],
        }

    client = AsyncOpenAI(api_key=api_key)
    response = await client.chat.completions.create(
        model=state.get("model", "gpt-4o"),
        messages=[
            {
                "role": "system",
                "content": "你是代码调试专家。分析错误并输出修复后的完整代码。",
            },
            {
                "role": "user",
                "content": (
                    f"原始代码:\n```{language}\n{current_code}\n```\n\n"
                    f"执行错误:\n{error}\n\n任务要求:\n{state.get('task', '')}\n\n请修复代码:"
                ),
            },
        ],
    )

    content = response.choices[0].message.content or ""
    fixed_code = extract_code_block(content)

    return {
        "fixed_code": fixed_code,
        "retry_count": state.get("retry_count", 0) + 1,
        "status": "fixing",
        "logs": [{"step": "Fixer", "message": "代码修复完成", "error": error}],
    }
