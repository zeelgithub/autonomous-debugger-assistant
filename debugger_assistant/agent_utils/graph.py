"""
LangGraph multi-agent orchestrator (PRODUCTION)
"""

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from .state import DebugState

from ..agents.planner import create_planner_agent
from ..agents.log_analyzer import create_log_analyzer_agent
from ..agents.code_navigator import create_code_navigator_agent
from ..agents.fix_generator import create_fix_generator_agent
from ..agents.test_runner import create_test_runner_agent
from ..agents.evaluator import create_evaluator_agent
from ..tools.patch_applier import patch_applier
from ..guardrails import input_guardrail, patch_guardrail
from ..tools.patcher import apply_patch

# ═══════════════════════════════════════
# ROUTER (Evaluator → control loop)
# ═══════════════════════════════════════
def patch_applier(state: DebugState):

    repo_path = state.get("repo_path")
    fix = state.get("proposed_fix", {})

    if not repo_path:
        return {
            "patch_results": {
                "status": "error",
                "reason": "Missing repo_path"
            }
        }

    file_results = []

    for file in fix.get("fixed_files", []):
        result = apply_patch(
            repo_path,
            file,
            fix.get("patch", "")
        )
        file_results.append(result)

    return {
        "patch_results": file_results,
        "messages": state.get("messages", []) + [
            {
                "role": "assistant",
                "content": f"Patch applied to {len(file_results)} file(s)"
            }
        ]
    }
def evaluator_router(state: DebugState) -> str:
    status = state.get("validation_status", "escalate")
    iteration = state.get("iteration", 0)
    max_iterations = state.get("max_iterations", 3)

    if status == "success":
        return END

    if status == "retry" and iteration < max_iterations:
        return "fix_generator"

    return END


# ═══════════════════════════════════════
# GRAPH BUILDER
# ═══════════════════════════════════════
llm = LLMConfig.get_default_model()
graph = get_graph(llm)
def build_graph(llm):
    graph = StateGraph(DebugState)

    # ─────────────────────────────
    # inject LLM into agents (BEST PRACTICE)
    # ─────────────────────────────
    planner_agent = create_planner_agent(llm)
    log_analyzer_agent = create_log_analyzer_agent(llm)
    code_navigator_agent = create_code_navigator_agent(llm)
    fix_generator_agent = create_fix_generator_agent(llm)
    test_runner_agent = create_test_runner_agent(llm)
    evaluator_agent = create_evaluator_agent(llm)

    # ─────────────────────────────
    # nodes
    # ─────────────────────────────
    graph.add_node("input_guardrail", input_guardrail)
    graph.add_node("planner", planner_agent)
    graph.add_node("log_analyzer", log_analyzer_agent)
    graph.add_node("code_navigator", code_navigator_agent)
    graph.add_node("fix_generator", fix_generator_agent)
    graph.add_node("patch_guardrail", patch_guardrail)
    graph.add_node("test_runner", test_runner_agent)
    graph.add_node("evaluator", evaluator_agent)
    graph.add_node("patch_applier", patch_applier)  
    # ─────────────────────────────
    # ENTRY FLOW
    # ─────────────────────────────
    graph.add_edge(START, "input_guardrail")
    graph.add_edge("input_guardrail", "planner")

    graph.add_edge("planner", "log_analyzer")
    graph.add_edge("log_analyzer", "code_navigator")
    graph.add_edge("code_navigator", "fix_generator")

    graph.add_edge("fix_generator", "patch_guardrail")
    graph.add_edge("patch_guardrail", "patch_applier")
    graph.add_edge("patch_applier", "test_runner")
    graph.add_edge("test_runner", "evaluator")

    
    # ─────────────────────────────
    # LOOP CONTROL (LangGraph conditional edges)
    # ─────────────────────────────
    graph.add_conditional_edges(
        "evaluator",
        evaluator_router,
        {
            "fix_generator": "fix_generator",
            END: END,
        },
    )

    # ─────────────────────────────
    # CHECKPOINTING (Memory)
    # ─────────────────────────────
    return graph.compile(checkpointer=MemorySaver())


# PUBLIC API
def get_graph(llm):
    return build_graph(llm)