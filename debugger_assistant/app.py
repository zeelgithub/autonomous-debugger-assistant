import streamlit as st
import uuid

from debugger_assistant.agent_utils.graph import get_graph
from debugger_assistant.agent_utils.provider import LLMConfig


st.title("🧠 Autonomous Debugger")


provider = st.selectbox("Choose Provider", ["ollama", "openai"])

model_name = st.text_input(
    "Model",
    value="llama3.2" if provider == "ollama" else "gpt-4o"
)

api_key = None
if provider == "openai":
    api_key = st.text_input("OpenAI API Key", type="password")


repo_url = st.text_input("Repo URL")
commit_sha = st.text_input("Commit SHA")

failed_test = st.text_input("Failed Test")
stack_trace = st.text_area("Stack Trace")
logs = st.text_area("Logs")


if st.button("Run Debugger"):

    model_identifier = f"{provider}:{model_name}"

    llm = LLMConfig.get_model(
        model_identifier=model_identifier,
        api_key=api_key if provider == "openai" else None,
    )

    graph = get_graph(llm)

    state = {
        "repo_url": repo_url,
        "commit_sha": commit_sha,
        "failed_test": failed_test,
        "stack_trace": stack_trace,
        "logs": logs,

        "debug_plan": [],
        "plan_status": "planning",

        "analysis_results": {},
        "code_analysis": {},
        "proposed_fix": {},
        "test_results": {},

        "validation_status": "retry",
        "evaluation_reason": "",

        "fix_attempts": [],

        "iteration": 0,
        "max_iterations": 3,

        "messages": [],

        "thread_id": str(uuid.uuid4()),
    }

    result = graph.invoke(
        state,
        config={"configurable": {"thread_id": state["thread_id"]}},
    )

    st.subheader("✅ Result")
    st.json(result)

    st.subheader("🧠 Messages")
    for msg in result["messages"]:
        st.write(msg)