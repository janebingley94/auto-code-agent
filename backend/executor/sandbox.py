from __future__ import annotations

import asyncio
import os
import tempfile
import time
from dataclasses import dataclass
from typing import Optional

from models.schemas import ExecutionResult


@dataclass
class SandboxConfig:
    timeout_seconds: int = 10
    max_output_size: int = 5_000


class CodeSandbox:
    def __init__(self, config: SandboxConfig | None = None) -> None:
        self.config = config or SandboxConfig()

    async def execute(self, code: str, language: str, stdin_input: Optional[str] = None) -> ExecutionResult:
        with tempfile.TemporaryDirectory() as tmpdir:
            code_file = self._write_code_file(tmpdir, code, language)
            try:
                result = await asyncio.wait_for(
                    self._run_code(code_file, language, tmpdir, stdin_input),
                    timeout=self.config.timeout_seconds,
                )
                return result
            except asyncio.TimeoutError:
                return ExecutionResult(
                    success=False,
                    output="",
                    error=f"Execution timed out after {self.config.timeout_seconds}s",
                    execution_time=float(self.config.timeout_seconds),
                    return_code=124,
                )

    def _write_code_file(self, tmpdir: str, code: str, language: str) -> str:
        extensions = {"python": "py", "javascript": "js", "typescript": "ts"}
        ext = extensions.get(language, "py")
        filepath = os.path.join(tmpdir, f"solution.{ext}")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(code)
        return filepath

    async def _run_code(
        self,
        code_file: str,
        language: str,
        tmpdir: str,
        stdin_input: Optional[str],
    ) -> ExecutionResult:
        commands = {
            "python": ["python3", code_file],
            "javascript": ["node", code_file],
            "typescript": ["ts-node", code_file],
        }
        cmd = commands.get(language, ["python3", code_file])

        start_time = time.time()
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=asyncio.subprocess.PIPE if stdin_input else None,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=tmpdir,
        )

        stdout, stderr = await proc.communicate(
            input=stdin_input.encode() if stdin_input else None
        )

        execution_time = time.time() - start_time
        output = stdout.decode(errors="ignore")[: self.config.max_output_size]
        error = stderr.decode(errors="ignore")[: self.config.max_output_size]

        success = proc.returncode == 0
        return ExecutionResult(
            success=success,
            output=output,
            error=error if not success else None,
            execution_time=execution_time,
            return_code=proc.returncode or 0,
        )
