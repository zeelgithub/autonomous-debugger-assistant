# debugger_assistant/tools/github.py

import os
import tempfile
from git import Repo


def clone_repo(repo_url: str) -> str:
    """
    Clones repo into a temp directory and returns local path.
    """
    temp_dir = tempfile.mkdtemp()
    Repo.clone_from(repo_url, temp_dir)
    return temp_dir


def list_repo_files(local_path: str):
    """
    Returns all files in repo.
    """
    files = []

    for root, _, filenames in os.walk(local_path):
        for f in filenames:
            full_path = os.path.join(root, f)
            rel_path = os.path.relpath(full_path, local_path)
            files.append(rel_path)

    return files