from __future__ import annotations

import json
from typing import Any, Dict

from openai import AsyncOpenAI

def _mock_plan(task: str) -> Dict[str, Any]:
    return {
        "plan": [
            "Parse requirements and define inputs/outputs",
            "Implement core logic with edge cases",
            "Add a simple CLI entrypoint and tests",
        ],
        "language": "python",
    }


async def planner_node(state: Dict[str, Any]) -> Dict[str, Any]:
    api_key = state.get("openai_api_key")
    if not api_key:
        data = _mock_plan(state["task"])
        return {
            "plan": data["plan"],
            "language": data["language"],
            "status": "planning",
            "logs": [
                {
                    "step": "Planner",
                    "message": "Mock plan generated (no API key)",
                    "plan": data["plan"],
                }
            ],
        }

    client = AsyncOpenAI(api_key=api_key)
    response = await client.chat.completions.create(
        model=state.get("model", "gpt-4o"),
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": (
                    "你是代码规划专家。将编程任务分解为清晰步骤。"
                    "返回JSON: {\"plan\": [\"step1\", ...], \"language\": \"python\"}"
                ),
            },
            {"role": "user", "content": f"任务: {state['task']}"},
        ],
    )
    payload = response.choices[0].message.content or "{}"
    data = json.loads(payload)

    return {
        "plan": data.get("plan", []),
        "language": data.get("language", "python"),
        "status": "planning",
        "logs": [{"step": "Planner", "message": "任务规划完成", "plan": data.get("plan", [])}],
    }
