"""
🛠 PATCH APPLIER (REAL EXECUTION LAYER)

Applies generated fix to repo and executes tests.
"""

import os
import subprocess
import tempfile
from typing import Dict, Any

from ..agent_utils.state import DebugState



def run_command(cmd: str, cwd: str):
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=120,
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)



def patch_applier(state: DebugState) -> Dict[str, Any]:
    repo_url = state["repo_url"]
    commit_sha = state["commit_sha"]
    fix = state.get("proposed_fix", {})

    patch = fix.get("patch", "")
    files = fix.get("fixed_files", [])

    if not patch or not files:
        return {
            "execution_status": "failed",
            "execution_logs": "No valid patch provided",
            "patch_applied": False,
        }


    with tempfile.TemporaryDirectory() as tmpdir:

        # Clone repo
        code, out, err = run_command(f"git clone {repo_url} .", tmpdir)
        if code != 0:
            return {
                "execution_status": "failed",
                "execution_logs": f"Git clone failed: {err}",
                "patch_applied": False,
            }

        # Checkout commit
        run_command(f"git checkout {commit_sha}", tmpdir)

        try:
            for file_path in files:
                full_path = os.path.join(tmpdir, file_path)

                # Ensure directory exists
                os.makedirs(os.path.dirname(full_path), exist_ok=True)

                # Overwrite file (LLM returns full snippet)
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(patch)

        except Exception as e:
            return {
                "execution_status": "failed",
                "execution_logs": f"Patch apply failed: {str(e)}",
                "patch_applied": False,
            }

   
        code, stdout, stderr = run_command("pytest -q", tmpdir)

        execution_logs = stdout + "\n" + stderr

        status = "success" if code == 0 else "failed"

        return {
            "execution_status": status,
            "execution_logs": execution_logs,
            "patch_applied": True,
            "messages": state.get("messages", []) + [
                {
                    "role": "assistant",
                    "content": f"Patch applied → tests {status}"
                }
            ],
        }