from __future__ import annotations

from typing import Any, Dict


async def executor_node(state: Dict[str, Any]) -> Dict[str, Any]:
    code = state.get("fixed_code") or state.get("generated_code", "")

    if not code:
        return {
            "execution_error": "No code to execute",
            "execution_result": None,
            "status": "testing",
            "logs": [{"step": "Executor", "message": "No code provided"}],
        }

    return {
        "execution_result": "Execution skipped in Phase 1 (mock).",
        "execution_error": None,
        "status": "testing",
        "logs": [{"step": "Executor", "message": "Mock execution complete"}],
    }
