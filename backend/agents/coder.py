from __future__ import annotations

from typing import Any, Dict

from openai import AsyncOpenAI

from tools.code_tools import extract_code_block


def _mock_code(task: str) -> str:
    return (
        "def solve():\n"
        "    \"\"\"Auto-generated placeholder solution.\"\"\"\n"
        "    print('Task:', '''" + task.replace("'", "\'") + "''')\n\n"
        "if __name__ == '__main__':\n"
        "    solve()\n"
    )


async def coder_node(state: Dict[str, Any]) -> Dict[str, Any]:
    api_key = state.get("openai_api_key")
    plan = state.get("plan", [])
    language = state.get("language", "python")

    if not api_key:
        code = _mock_code(state["task"])
        return {
            "generated_code": code,
            "status": "coding",
            "logs": [{"step": "Coder", "message": "Mock code generated (no API key)", "code_preview": code[:200]}],
        }

    client = AsyncOpenAI(api_key=api_key)
    plan_text = "\n".join([f"{i+1}. {step}" for i, step in enumerate(plan)])

    response = await client.chat.completions.create(
        model=state.get("model", "gpt-4o"),
        messages=[
            {
                "role": "system",
                "content": (
                    f"你是专业的{language}开发者。\n"
                    "根据计划编写完整可运行代码，包含注释和边界处理。"
                    "只输出代码，不要解释。"
                ),
            },
            {"role": "user", "content": f"任务: {state['task']}\n\n执行计划:\n{plan_text}"},
        ],
    )

    content = response.choices[0].message.content or ""
    code = extract_code_block(content)

    return {
        "generated_code": code,
        "status": "coding",
        "logs": [{"step": "Coder", "message": "代码生成完成", "code_preview": code[:200]}],
    }
