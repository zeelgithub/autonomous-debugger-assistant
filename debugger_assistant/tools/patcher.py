"""
🛠 Patch Applier Tool (REAL FILE MODIFICATION)

Applies generated fixes directly into repository files.
"""

import os
from typing import Dict, Any


def apply_patch(repo_path: str, file_path: str, patch: str) -> Dict[str, Any]:
    """
    Applies patch to a file inside repo.

    NOTE:
    - This assumes patch is full file content OR minimal replacement code
    """

    try:
        full_path = os.path.join(repo_path, file_path.lstrip("/"))

        if not os.path.exists(full_path):
            return {
                "status": "error",
                "reason": f"File not found: {file_path}"
            }

        # backup (VERY IMPORTANT for safety)
        backup_path = full_path + ".bak"
        with open(full_path, "r", encoding="utf-8") as f:
            original = f.read()

        with open(backup_path, "w", encoding="utf-8") as f:
            f.write(original)

        # write patch
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(patch)

        return {
            "status": "success",
            "file": file_path,
            "backup": backup_path
        }

    except Exception as e:
        return {
            "status": "error",
            "reason": str(e)
        }