"""
🔧 FIX GENERATOR AGENT (Executor)
"""

from typing import Dict, Any, List

from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

from ..agent_utils.provider import LLMConfig
from ..agent_utils.state import DebugState
from ..guardrails import llm_guardrail



class FixProposal(BaseModel):
    patch: str
    fixed_files: List[str]
    explanation: str
    risk_level: str



FIX_GENERATOR_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You are a senior software engineer.

Generate minimal safe fix only.

Rules:
- do NOT rewrite full files
- minimal patch only
- production safe

IMPORTANT:
Return FULL corrected function or file snippet.
Do NOT return git diff format.
Return JSON only.
"""
    ),
    (
        "human",
        """
ERROR ANALYSIS:
{analysis_results}

CODE CONTEXT:
{code_analysis}

STACK TRACE:
{stack_trace}

Generate fix.
"""
    ),
])



def create_fix_generator_agent(llm):

    fix_chain = (
        FIX_GENERATOR_PROMPT
        | llm.with_structured_output(FixProposal)
    )

    def fix_generator_agent(state: DebugState):

        result: FixProposal = fix_chain.invoke({
            "analysis_results": state.get("analysis_results", {}),
            "code_analysis": state.get("code_analysis", {}),
            "stack_trace": state["stack_trace"],
        })

        if not llm_guardrail(result.patch):
            return {
                "proposed_fix": {
                    "patch": "",
                    "fixed_files": [],
                    "explanation": "Blocked by guardrail",
                    "risk_level": "high",
                },
                "validation_status": "retry",
                "evaluation_reason": "Unsafe patch blocked",
                "messages": state.get("messages", []) + [
                    {
                        "role": "assistant",
                        "content": "Guardrail blocked unsafe fix"
                    }
                ],
            }

      
        return {
            "proposed_fix": {
                "patch": result.patch,
                "fixed_files": result.fixed_files,
                "explanation": result.explanation,
                "risk_level": result.risk_level,
            },
            "messages": state.get("messages", []) + [
                {
                    "role": "assistant",
                    "content": f"Fix generated for {len(result.fixed_files)} file(s)"
                }
            ],
        }

    return fix_generator_agent