from __future__ import annotations

from langgraph.graph import END, StateGraph

from agents.coder import coder_node
from agents.executor import executor_node
from agents.fixer import fixer_node
from agents.finalizer import finalizer_node
from agents.planner import planner_node
from agents.tester import tester_node
from models.schemas import CodeAgentState

MAX_RETRIES = 3


def should_fix_or_finalize(state: CodeAgentState) -> str:
    if state.get("execution_error"):
        if state.get("retry_count", 0) >= MAX_RETRIES:
            return "failed"
        return "fix"
    return "finalize"


def build_code_graph():
    workflow = StateGraph(CodeAgentState)

    workflow.add_node("planner", planner_node)
    workflow.add_node("coder", coder_node)
    workflow.add_node("executor", executor_node)
    workflow.add_node("tester", tester_node)
    workflow.add_node("fixer", fixer_node)
    workflow.add_node("finalizer", finalizer_node)

    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "coder")
    workflow.add_edge("coder", "executor")
    workflow.add_edge("executor", "tester")

    workflow.add_conditional_edges(
        "tester",
        should_fix_or_finalize,
        {
            "fix": "fixer",
            "finalize": "finalizer",
            "failed": END,
        },
    )

    workflow.add_edge("fixer", "executor")
    workflow.add_edge("finalizer", END)

    return workflow.compile()
