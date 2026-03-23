"""
🧪 Real Test Execution Tool (pytest-based)

Runs actual tests in cloned repository.
"""

import subprocess
from typing import Dict, Any


def run_pytest(repo_path: str) -> Dict[str, Any]:
    """
    Executes pytest inside the repository.
    """

    try:
        result = subprocess.run(
            ["pytest", "-q"],
            cwd=repo_path,
            capture_output=True,
            text=True
        )

        output = result.stdout + "\n" + result.stderr

        return {
            "status": "passed" if result.returncode == 0 else "failed",
            "return_code": result.returncode,
            "output": output,
            "passed": result.returncode == 0,
        }

    except FileNotFoundError:
        return {
            "status": "error",
            "output": "pytest not installed or not found",
            "passed": False,
        }