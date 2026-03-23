from debugger_assistant.agent_utils.graph import get_graph
from debugger_assistant.agent_utils.provider import LLMConfig
import uuid


def main():

    llm = LLMConfig.get_model(
        provider="ollama",
        model="llama3.1:8b",
    )

    graph = get_graph(llm)

    state = {
    "repo_url": "https://github.com/example/repo",
    "commit_sha": "abc123",
    "failed_test": "test_login_failure",
    "stack_trace": "File 'app.py', line 42, NameError",
    "logs": "Traceback ...",

    # REQUIRED for LangGraph stability
    "debug_plan": [],
    "plan_status": "planning",
    "analysis_results": {},
    "code_analysis": {},
    "proposed_fix": None,
    "test_results": {},

    "validation_status": "retry",
    "evaluation_reason": "",
    "fix_attempts": [],

    "iteration": 0,
    "max_iterations": 3,

    "messages": [],
    "thread_id": str(uuid.uuid4()),
}

    print("\n🚀 Running Autonomous Debugger...\n")


    result = graph.invoke(
    state,
    config={
        "configurable": {
            "thread_id": state["thread_id"]
        }
    }
)

    print("\n✅ FINAL RESULT:\n")
    print(result)


if __name__ == "__main__":
    main()