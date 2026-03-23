# Auto Code Agent (Phase 1)

自动写代码 Agent（AutoGPT 风格）核心循环实现：任务规划 → 代码生成 → 执行 → 测试 → 修复 → 结果整理。

## 目录结构
```
auto-code-agent/
├── backend/   # Phase 1 core agent
└── frontend/  # 占位目录
```

## Phase 1 范围
- 5 个 Agent 节点 (planner/coder/executor/tester/fixer)
- LangGraph StateGraph 构建 + 条件边
- 无 API key 时提供 Mock 结果

## Phase 2 代码执行沙箱
- 默认使用 subprocess 沙箱执行（10s 超时，5KB 输出上限）
- 支持语言：Python / JavaScript / TypeScript（TypeScript 需安装 `ts-node`）
- 可选 Docker 执行：在 state 中设置 `use_docker=True`

## 运行后端
```
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

## 简单测试
在 Python 里调用：
```python
from graph.code_graph import build_code_graph

workflow = build_code_graph()
state = {
  "task": "Write a function that sums a list",
  "task_id": "demo",
  "openai_api_key": None,
  "retry_count": 0,
  "logs": []
}

result = await workflow.ainvoke(state)
print(result["final_code"])
```

或使用 CLI：
```bash
cd backend
python run_agent.py "Write a function that sums a list"
```
