from __future__ import annotations

from typing import Any, Dict


async def finalizer_node(state: Dict[str, Any]) -> Dict[str, Any]:
    final_code = state.get("fixed_code") or state.get("generated_code", "")
    return {
        "final_code": final_code,
        "status": "done",
        "logs": [{"step": "Finalizer", "message": "Final code prepared"}],
    }
