#!/usr/bin/env python3
"""Generate the shared HTML/PDF profile for a PR build (JSON is valid YAML)."""
import json
import os
from pathlib import Path

number = int(os.environ["PR_NUMBER"])
sha = os.environ["PR_SHA"]
url = f"https://nggong.github.io/docs/pr/{number}"
Path("_quarto-pr-preview.yml").write_text(json.dumps({
    "website": {
        "site-url": url + "/",
        "repo-branch": os.environ["PR_BRANCH"],
        "announcement": {
            "content": f"PR #{number} preview — commit {sha[:12]}. Proposed changes for review.",
            "type": "warning",
            "dismissable": False,
        },
    },
    "published-site-url": url,
}, indent=2) + "\n")
