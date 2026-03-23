from __future__ import annotations

import json
import os
from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from redis.asyncio import Redis


class TaskStore(ABC):
    @abstractmethod
    async def create_task(self, task_id: str, payload: dict) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update_task(self, task_id: str, payload: dict) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_task(self, task_id: str) -> Optional[dict]:
        raise NotImplementedError

    @abstractmethod
    async def list_tasks(self) -> List[dict]:
        raise NotImplementedError


class MemoryTaskStore(TaskStore):
    def __init__(self) -> None:
        self._store: Dict[str, dict] = {}

    async def create_task(self, task_id: str, payload: dict) -> None:
        self._store[task_id] = payload

    async def update_task(self, task_id: str, payload: dict) -> None:
        self._store[task_id] = payload

    async def get_task(self, task_id: str) -> Optional[dict]:
        return self._store.get(task_id)

    async def list_tasks(self) -> List[dict]:
        return list(self._store.values())[::-1]


class RedisTaskStore(TaskStore):
    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    async def create_task(self, task_id: str, payload: dict) -> None:
        await self.redis.set(self._key(task_id), json.dumps(payload))

    async def update_task(self, task_id: str, payload: dict) -> None:
        await self.redis.set(self._key(task_id), json.dumps(payload))

    async def get_task(self, task_id: str) -> Optional[dict]:
        data = await self.redis.get(self._key(task_id))
        if not data:
            return None
        return json.loads(data)

    async def list_tasks(self) -> List[dict]:
        keys = await self.redis.keys("task:*")
        tasks: List[dict] = []
        for key in keys:
            data = await self.redis.get(key)
            if data:
                tasks.append(json.loads(data))
        tasks.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return tasks

    def _key(self, task_id: str) -> str:
        return f"task:{task_id}"


async def get_task_store() -> TaskStore:
    url = os.getenv("REDIS_URL")
    if not url:
        return MemoryTaskStore()

    try:
        redis = Redis.from_url(url, decode_responses=True)
        await redis.ping()
        return RedisTaskStore(redis)
    except Exception:
        return MemoryTaskStore()
