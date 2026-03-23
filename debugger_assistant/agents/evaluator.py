"""
🥉 EVALUATOR AGENT (Control Plane)

Decides:
- success → END
- retry → fix_generator
- escalate → END
"""

from typing import Dict, Any, List

from pydantic import BaseModel, Field

from langchain_core.prompts import ChatPromptTemplate

from ..agent_utils.provider import LLMConfig
from ..agent_utils.state import DebugState



class EvaluationResult(BaseModel):
    """Final decision from evaluator."""

    validation_status: str = Field(
        ...,
        description="success | retry | escalate"
    )

    evaluation_reason: str = Field(
        ...,
        description="Reason for decision"
    )

    confidence: float = Field(
        ...,
        ge=0,
        le=1,
        description="Confidence score (0–1)"
    )



EVALUATOR_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You are a senior software engineering evaluator.

Your job is to decide whether an automated fix is correct.

DECISION RULES:

1. SUCCESS:
- All tests pass
- Root cause is clearly addressed
- Fix is minimal and safe

2. RETRY:
- Tests fail but issue is likely fixable
- Root cause is identified but fix is incomplete

3. ESCALATE:
- Ambiguous root cause
- Multiple conflicting failures
- Requires human intervention

Be strict and realistic.

Return structured JSON only.
"""
    ),
    (
        "human",
        """
TEST RESULTS:
{test_results}

ROOT CAUSE ANALYSIS:
{analysis_results}

PROPOSED FIX:
{proposed_fix}

FIX ATTEMPTS:
{fix_attempts}
"""
    ),
])

def create_evaluator_agent(llm):

    evaluator_chain = (
        EVALUATOR_PROMPT
        | llm.with_structured_output(EvaluationResult)
    )

    def evaluator_agent(state: DebugState):

        result: EvaluationResult = evaluator_chain.invoke({
            "test_results": state.get("test_results", {}),
            "analysis_results": state.get("analysis_results", {}),
            "proposed_fix": state.get("proposed_fix", {}),
            "fix_attempts": state.get("fix_attempts", []),
        })


        status = result.validation_status.lower().strip()

        if status not in ["success", "retry", "escalate"]:
            status = "escalate"  # safe fallback


        iteration = state.get("iteration", 0) + 1

      
        fix_attempts = state.get("fix_attempts", [])
        fix_attempts.append({
            "iteration": iteration,
            "status": status,
            "reason": result.evaluation_reason,
            "confidence": result.confidence,
        })

    
        return {
            "validation_status": status,
            "evaluation_reason": result.evaluation_reason,
            "iteration": iteration,
            "fix_attempts": fix_attempts,
            "messages": state.get("messages", []) + [
                {
                    "role": "assistant",
                    "content": f"Evaluation: {status} → {result.evaluation_reason}"
                }
            ],
        }

    return evaluator_agent