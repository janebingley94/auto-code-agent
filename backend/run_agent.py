import argparse
import asyncio
import json

from graph.code_graph import build_code_graph


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run auto code agent graph")
    parser.add_argument("task", help="Task description")
    parser.add_argument("--language", default="python", help="Target language")
    parser.add_argument("--openai-api-key", default=None, help="OpenAI API key")
    parser.add_argument("--model", default="gpt-4o", help="Model name")
    return parser.parse_args()


async def main() -> None:
    args = parse_args()
    graph = build_code_graph()
    state = {
        "task": args.task,
        "task_id": "cli",
        "language": args.language,
        "openai_api_key": args.openai_api_key,
        "model": args.model,
        "retry_count": 0,
        "logs": [],
    }

    result = await graph.ainvoke(state)
    print("=== FINAL CODE ===")
    print(result.get("final_code", ""))
    print("=== STATUS ===")
    print(result.get("status"))
    print("=== LOGS ===")
    print(json.dumps(result.get("logs", []), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
