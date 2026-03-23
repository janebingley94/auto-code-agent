from __future__ import annotations

import tempfile
from typing import Optional

try:
    import docker
except Exception:  # pragma: no cover - optional dependency
    docker = None

from models.schemas import ExecutionResult


class DockerExecutor:
    IMAGES = {
        "python": "python:3.11-slim",
        "javascript": "node:20-alpine",
        "typescript": "node:20-alpine",
    }

    def __init__(self) -> None:
        if docker is None:
            raise RuntimeError("Docker SDK not installed. pip install docker")
        self.client = docker.from_env()

    def execute(self, code: str, language: str, stdin_input: Optional[str] = None) -> ExecutionResult:
        image = self.IMAGES.get(language, "python:3.11-slim")
        command = self._command_for(language)

        with tempfile.TemporaryDirectory() as tmpdir:
            code_file = f"{tmpdir}/solution.{self._ext(language)}"
            with open(code_file, "w", encoding="utf-8") as f:
                f.write(code)

            try:
                output = self.client.containers.run(
                    image=image,
                    command=command,
                    volumes={tmpdir: {"bind": "/code", "mode": "ro"}},
                    network_disabled=True,
                    mem_limit="256m",
                    cpu_period=100000,
                    cpu_quota=50000,
                    remove=True,
                    detach=False,
                    stdin_open=bool(stdin_input),
                    tty=False,
                )
                decoded = output.decode() if hasattr(output, "decode") else str(output)
                return ExecutionResult(
                    success=True,
                    output=decoded,
                    error=None,
                    execution_time=0.0,
                    return_code=0,
                )
            except Exception as exc:  # pragma: no cover
                return ExecutionResult(
                    success=False,
                    output="",
                    error=str(exc),
                    execution_time=0.0,
                    return_code=1,
                )

    def _ext(self, language: str) -> str:
        return {"python": "py", "javascript": "js", "typescript": "ts"}.get(language, "py")

    def _command_for(self, language: str) -> str:
        if language == "javascript":
            return "node /code/solution.js"
        if language == "typescript":
            return "node /code/solution.ts"
        return "python /code/solution.py"
