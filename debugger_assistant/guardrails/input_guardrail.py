"""
🛡 Input Guardrail - Validates incoming CI data
"""

from typing import Dict, Any
from ..agent_utils.state import DebugState


def input_guardrail(state: dict):
    missing = []

    if not state.get("stack_trace"):
        missing.append("stack_trace")

    if not state.get("logs"):
        missing.append("logs")

    if missing:
        return {
            **state,
            "validation_status": "failed",
            "evaluation_reason": f"Missing fields: {missing}"
        }

    return state