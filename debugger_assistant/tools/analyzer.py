"""
🔧 Stack Trace Analyzer Tool
"""

from typing import Dict, Any
import re


def parse_stack_trace(stack_trace: str) -> Dict[str, Any]:
    """
    Extract file paths and line numbers from stack trace.
    """

    pattern = r'File "(.+?)", line (\d+)'
    matches = re.findall(pattern, stack_trace)

    return {
        "files": [m[0] for m in matches],
        "lines": [int(m[1]) for m in matches],
    }