from __future__ import annotations

import asyncio
import json
import uuid
from typing import AsyncGenerator, List

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from models.schemas import TaskRequest, TaskResponse
from services.runner import run_code_agent
from services.task_store import get_task_store

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=TaskResponse)
async def create_task(request: TaskRequest) -> TaskResponse:
    store = await get_task_store()
    task_id = str(uuid.uuid4())

    payload = {
        "id": task_id,
        "task": request.task,
        "language": request.language,
        "status": "queued",
        "plan": [],
        "generated_code": "",
        "test_code": "",
        "final_code": "",
        "execution_result": None,
        "retry_count": 0,
        "logs": [],
        "created_at": None,
        "completed_at": None,
    }

    await store.create_task(task_id, payload)
    asyncio.create_task(run_code_agent(task_id, request.task, request.language, store))
    return TaskResponse(task_id=task_id)


@router.get("/{task_id}")
async def get_task(task_id: str) -> dict:
    store = await get_task_store()
    record = await store.get_task(task_id)
    if not record:
        raise HTTPException(status_code=404, detail="Task not found")
    return record


@router.get("")
async def list_tasks() -> List[dict]:
    store = await get_task_store()
    return await store.list_tasks()


@router.get("/{task_id}/stream")
async def stream_task(task_id: str) -> StreamingResponse:
    store = await get_task_store()

    async def generate() -> AsyncGenerator[bytes, None]:
        while True:
            record = await store.get_task(task_id)
            if record:
                data = json.dumps(record, ensure_ascii=False)
                yield f"data: {data}\n\n".encode()
                if record.get("status") in {"done", "failed"}:
                    break
            await asyncio.sleep(0.5)
        yield b"data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
