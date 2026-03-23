from __future__ import annotations

from typing import Any, Dict

from executor.sandbox import CodeSandbox


async def executor_node(state: Dict[str, Any]) -> Dict[str, Any]:
    code = state.get("fixed_code") or state.get("generated_code", "")
    language = state.get("language", "python")
    stdin_input = state.get("stdin_input")

    if not code:
        return {
            "execution_error": "No code to execute",
            "execution_result": None,
            "status": "testing",
            "logs": [{"step": "Executor", "message": "No code provided"}],
        }

    use_docker = bool(state.get("use_docker"))
    if use_docker:
        try:
            from executor.docker_executor import DockerExecutor

            executor = DockerExecutor()
            result = executor.execute(code, language, stdin_input=stdin_input)
        except Exception as exc:  # pragma: no cover
            return {
                "execution_error": str(exc),
                "execution_result": None,
                "status": "testing",
                "logs": [{"step": "Executor", "message": "Docker execution failed", "error": str(exc)}],
            }
    else:
        sandbox = CodeSandbox()
        result = await sandbox.execute(code, language, stdin_input=stdin_input)

    return {
        "execution_result": result.output if result.success else None,
        "execution_error": result.error,
        "status": "testing",
        "logs": [
            {
                "step": "Executor",
                "message": "Execution complete" if result.success else "Execution failed",
                "duration": result.execution_time,
                "return_code": result.return_code,
                "output_preview": result.output[:200],
            }
        ],
    }
