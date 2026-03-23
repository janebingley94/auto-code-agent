from __future__ import annotations

from typing import Any, Dict

from openai import AsyncOpenAI

from tools.code_tools import extract_code_block


def _mock_tests() -> str:
    return (
        "def test_placeholder():\n"
        "    assert 1 + 1 == 2\n"
    )


async def tester_node(state: Dict[str, Any]) -> Dict[str, Any]:
    api_key = state.get("openai_api_key")
    language = state.get("language", "python")

    if not api_key:
        test_code = _mock_tests()
        return {
            "test_code": test_code,
            "status": "testing",
            "logs": [{"step": "Tester", "message": "Mock tests generated", "test_preview": test_code[:200]}],
        }

    client = AsyncOpenAI(api_key=api_key)
    response = await client.chat.completions.create(
        model=state.get("model", "gpt-4o"),
        messages=[
            {
                "role": "system",
                "content": (
                    f"你是{language}测试工程师。\n"
                    "为代码生成最小可运行测试。只输出测试代码，不要解释。"
                ),
            },
            {"role": "user", "content": state.get("generated_code", "")},
        ],
    )

    content = response.choices[0].message.content or ""
    test_code = extract_code_block(content)

    return {
        "test_code": test_code,
        "status": "testing",
        "logs": [{"step": "Tester", "message": "测试生成完成", "test_preview": test_code[:200]}],
    }
