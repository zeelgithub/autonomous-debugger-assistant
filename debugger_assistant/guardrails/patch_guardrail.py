"""
🛡 Patch Guardrail - Validates generated fixes
"""

from typing import Dict, Any
from ..agent_utils.state import DebugState


def patch_guardrail(state: DebugState) -> Dict[str, Any]:
    fix = state.get("proposed_fix", {})
    files = state.get("code_analysis", {}).get("affected_files", [])

    if not files:
        return {
            "validation_status": "retry",
            "evaluation_reason": "No affected files"
        }

    if "rm -rf" in str(fix):
        return {
            "validation_status": "retry",
            "evaluation_reason": "Unsafe patch detected"
        }

    return state