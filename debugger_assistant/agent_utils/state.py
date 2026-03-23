"""🧠 LangGraph Debug State (Production Ready)"""

from typing import List, Dict, Any, Optional
from typing_extensions import TypedDict, Annotated, Literal

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class DebugState(TypedDict, total=False):
 
    repo_url: str
    commit_sha: str
    failed_test: str
    stack_trace: str
    logs: str

  
    debug_plan: List[str]
    plan_status: Literal["planning", "executing", "done"]


    analysis_results: Dict[str, Any]
    code_analysis: Dict[str, Any]
    proposed_fix: Dict[str, Any]
    test_results: Dict[str, Any]

   
    patch_applied: bool
    execution_status: Literal["pending", "running", "success", "failed"]
    execution_logs: str

  
    validation_status: Literal["success", "retry", "escalate"]
    evaluation_reason: str


    iteration: int
    max_iterations: int
    fix_attempts: List[Dict[str, Any]]

    messages: Annotated[list[BaseMessage], add_messages]

   
    thread_id: str