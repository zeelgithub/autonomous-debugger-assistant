"""
🔧 LOG ANALYZER AGENT (Executor Node)

Extracts:
- root cause
- error type
- failure signals
- stack trace insights

This is a deterministic reasoning enrichment step.
"""

from typing import Dict, Any, List

from pydantic import BaseModel, Field

from langchain_core.prompts import ChatPromptTemplate

from ..agent_utils.provider import LLMConfig
from ..agent_utils.state import DebugState



class LogAnalysis(BaseModel):
    """Structured log understanding output."""

    error_type: str = Field(
        ...,
        description="Type of error (e.g., AssertionError, NullPointer, ImportError)"
    )

    root_cause: str = Field(
        ...,
        description="Most likely root cause of failure"
    )

    severity: str = Field(
        ...,
        description="low | medium | high | critical"
    )

    affected_components: List[str] = Field(
        default_factory=list,
        description="Modules/files likely involved"
    )

    summary: str = Field(
        ...,
        description="Concise explanation of the failure"
    )



LOG_ANALYZER_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You are a senior debugging engineer specialized in log analysis.

Your job:
- Analyze stack traces and logs
- Identify root cause of failure
- Classify error type accurately
- Identify affected system components

RULES:
- Be precise, not verbose
- Prefer root cause over symptoms
- Ignore irrelevant log noise
- Focus on first meaningful error in stack trace

Return structured JSON only.
"""
    ),
    (
        "human",
        """
FAILED TEST:
{failed_test}

STACK TRACE:
{stack_trace}

LOGS:
{logs}

Repo:
{repo_url}
Commit:
{commit_sha}

Analyze this failure.
"""
    ),
])


def create_log_analyzer_agent(llm):

    log_analysis_chain = (
        LOG_ANALYZER_PROMPT
        | llm.with_structured_output(LogAnalysis)
    )

    def log_analyzer_agent(state: DebugState):

        result: LogAnalysis = log_analysis_chain.invoke({
            "failed_test": state["failed_test"],
            "stack_trace": state["stack_trace"],
            "logs": state["logs"],
            "repo_url": state["repo_url"],
            "commit_sha": state["commit_sha"],
        })

        return {
            "analysis_results": {
                "error_type": result.error_type,
                "root_cause": result.root_cause,
                "severity": result.severity,
                "affected_components": result.affected_components,
                "summary": result.summary,
            },
            "messages": state.get("messages", []) + [
                {
                    "role": "assistant",
                    "content": f"Log analysis complete: {result.error_type}"
                }
            ],
        }

    return log_analyzer_agent