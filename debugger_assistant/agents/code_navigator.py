"""
🔧 CODE NAVIGATOR AGENT (Executor)
"""

from typing import Dict, Any, List

from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

from ..tools.github import clone_repo, list_repo_files
from ..agent_utils.state import DebugState


class CodeAnalysis(BaseModel):
    affected_files: List[str]
    affected_functions: List[str] = []
    line_numbers: Dict[str, List[int]] = {}
    reasoning: str




CODE_NAVIGATOR_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You are a senior software engineer specialized in debugging.

Map stack traces → files and functions.

Rules:
- Use ONLY provided repo files
- Do NOT hallucinate files
- Return top 1–3 likely files
"""
    ),
    (
        "human",
        """
ERROR:
{error_analysis}

STACK TRACE:
{stack_trace}

FILES:
{repo_files}
"""
    ),
])



def create_code_navigator_agent(llm):

    chain = (
        CODE_NAVIGATOR_PROMPT
        | llm.with_structured_output(CodeAnalysis)
    )

    def code_navigator_agent(state: DebugState):

        repo_path = clone_repo(state["repo_url"])

        repo_files = list_repo_files(repo_path)[:100]

        result: CodeAnalysis = chain.invoke({
            "error_analysis": state.get("analysis_results", {}),
            "stack_trace": state["stack_trace"],
            "repo_files": repo_files,
        })

        return {
            "code_analysis": {
                "affected_files": result.affected_files,
                "affected_functions": result.affected_functions,
                "line_numbers": result.line_numbers,
                "reasoning": result.reasoning,
            },
            "repo_path": repo_path,
            "messages": state.get("messages", []) + [
                {
                    "role": "assistant",
                    "content": f"Code navigation complete: {len(result.affected_files)} files identified"
                }
            ],
        }

    return code_navigator_agent