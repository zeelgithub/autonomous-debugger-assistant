"""
🧪 TEST RUNNER AGENT (Executor)

Purpose:
- Validate proposed fix using test execution results
- Extract failure signals from CI / local runs
- Provide structured feedback to evaluator
"""

from typing import Dict, Any, List

from pydantic import BaseModel, Field

from langchain_core.prompts import ChatPromptTemplate

from ..agent_utils.provider import LLMConfig
from ..agent_utils.state import DebugState
from ..tools.tester import run_pytest   



class TestReport(BaseModel):
    """Structured test execution result."""

    status: str = Field(
        ...,
        description="success | failure | partial"
    )

    passed_tests: List[str] = Field(
        default_factory=list,
        description="List of passing tests"
    )

    failed_tests: List[str] = Field(
        default_factory=list,
        description="List of failing tests"
    )

    failure_reason: str = Field(
        ...,
        description="Primary reason for failure (if any)"
    )

    confidence: float = Field(
        ...,
        description="Confidence score (0-1) that fix is correct"
    )


TEST_RUNNER_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You are a QA engineer responsible for validating code fixes.

Your job:
- Analyze test execution results
- Determine if fix is valid
- Identify remaining failures
- Provide structured evaluation

RULES:
- Be strict and realistic
- A fix is ONLY successful if all critical tests pass
- Identify root cause of remaining failures if any
- Do not assume success unless clearly indicated

Return structured JSON only.
"""
    ),
    (
        "human",
        """
PROPOSED FIX:
{proposed_fix}

CODE CONTEXT:
{code_analysis}

ORIGINAL ERROR:
{analysis_results}

TASK:
Evaluate whether the fix resolves the issue.
"""
    ),
])



def create_test_runner_agent(llm):

    def test_runner_agent(state: DebugState):

        repo_path = state.get("repo_path")

        if not repo_path:
            return {
                "test_results": {
                    "status": "error",
                    "reason": "repo_path missing"
                }
            }

        result = run_pytest(repo_path)

        return {
            "test_results": {
                "status": result["status"],
                "output": result["output"],
                "return_code": result.get("return_code"),
            },
            "messages": state.get("messages", []) + [
                {
                    "role": "assistant",
                    "content": f"Tests executed: {result['status']}"
                }
            ],
        }

    return test_runner_agent