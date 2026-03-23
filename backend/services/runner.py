from __future__ import annotations

from datetime import datetime

from graph.code_graph import build_code_graph
from models.schemas import CodeAgentState
from services.task_store import TaskStore


async def run_code_agent(task_id: str, task: str, language: str, store: TaskStore) -> None:
    graph = build_code_graph()
    state: CodeAgentState = {
        "task": task,
        "task_id": task_id,
        "language": language,
        "retry_count": 0,
        "logs": [],
        "status": "planning",
        "created_at": datetime.utcnow().isoformat(),
    }

    await store.update_task(task_id, dict(state))

    try:
        result = await graph.ainvoke(state)
        result["status"] = result.get("status", "done")
        result["completed_at"] = datetime.utcnow().isoformat()
        await store.update_task(task_id, result)
    except Exception as exc:  # pragma: no cover
        state["status"] = "failed"
        state["execution_error"] = str(exc)
        state["completed_at"] = datetime.utcnow().isoformat()
        await store.update_task(task_id, dict(state))
