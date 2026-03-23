"""
🥇 PLANNER AGENT (LangGraph + Context Engineering Best Practices)

Converts CI failure → structured debug plan
"""

from typing import List, Dict, Any

from pydantic import BaseModel, Field

from langchain_core.prompts import ChatPromptTemplate
from ..agent_utils.provider import LLMConfig
from ..agent_utils.state import DebugState


# ═══════════════════════════════════════════════════════
# 🧠 STRUCTURED OUTPUT (LATEST PATTERN)
# ═══════════════════════════════════════════════════════

class DebugPlan(BaseModel):
    """Structured debugging plan output."""

    steps: List[str] = Field(
        ...,
        description="Ordered execution steps for debugging"
    )

    priority_files: List[str] = Field(
        default_factory=list,
        description="Files most likely related to failure"
    )

    reasoning: str = Field(
        ...,
        description="Why this plan was created"
    )


# ═══════════════════════════════════════════════════════
# 🧠 CONTEXT ENGINEERED PROMPT (BEST PRACTICE)
# ═══════════════════════════════════════════════════════

PLANNER_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You are a senior software debugging planner.

You analyze CI failures and generate structured execution plans for autonomous agents.

RULES:
- Be precise and deterministic
- Prefer minimal steps
- Focus on root cause, not symptoms
- Always consider stack trace first
- Always output structured JSON

AVAILABLE ACTIONS:
1. analyze error
2. locate file
3. trace dependency
4. suggest fix
5. run tests

Return a structured debugging plan.
"""
    ),
    (
        "human",
        """
CI FAILURE CONTEXT:

Repository: {repo_url}
Commit: {commit_sha}

Failed Test:
{failed_test}

Stack Trace:
{stack_trace}

Logs:
{logs}

Create an optimal debugging plan.
"""
    ),
])


# ═══════════════════════════════════════════════════════
# 🤖 LLM INITIALIZATION (LangGraph Compatible)
# ═══════════════════════════════════════════════════════







# ═══════════════════════════════════════════════════════
# 🧠 LANGGRAPH NODE FUNCTION
# ═══════════════════════════════════════════════════════

def create_planner_agent(llm):

    planner_chain = (
        PLANNER_PROMPT
        | llm.with_structured_output(DebugPlan)
    )

    def planner_agent(state):
        result = planner_chain.invoke({
            "repo_url": state.get("repo_url", ""),
            "commit_sha": state.get("commit_sha", ""),
            "failed_test": state.get("failed_test", ""),
            "stack_trace": state.get("stack_trace", ""),
            "logs": state.get("logs", "")
        })

        return {
            "debug_plan": result.steps,
            "plan_status": "executing",
        }

    return planner_agent