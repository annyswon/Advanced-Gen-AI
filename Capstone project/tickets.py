# tickets.py — GitHub ticket creation with auto-labels + original query

import os
import requests

def create_ticket(title: str, description: str, user_name: str, user_email: str, user_query: str = None):
    """
    Create a GitHub Issue in the repo set by env var GITHUB_REPO.
    Requires secrets: GITHUB_TOKEN, GITHUB_REPO.
    Auto-adds 'support' label and includes the original user query.
    """
    token = os.getenv("GITHUB_TOKEN")
    repo  = os.getenv("GITHUB_REPO", "annyswon/Advanced-Gen-AI")

    if not token or not repo:
        return False, "Missing GITHUB_TOKEN or GITHUB_REPO in environment."

    url = f"https://api.github.com/repos/{repo}/issues"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    # Build issue body
    body_lines = []
    if user_query:
        body_lines.append(f"**User query:** {user_query}\n")
    if description:
        body_lines.append(f"**Details provided by user:**\n{description}\n")
    body_lines.append(f"**Reporter:** {user_name} <{user_email}>")

    payload = {
        "title": title,
        "body": "\n\n".join(body_lines),
        "labels": ["support"]
    }

    r = requests.post(url, headers=headers, json=payload)
    if r.status_code in (200, 201):
        return True, r.json().get("html_url")
    return False, f"GitHub error {r.status_code}: {r.text}"
