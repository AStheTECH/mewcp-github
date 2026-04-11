from __future__ import annotations

from typing import Any

import httpx

from .config import GITHUB_API_BASE


def _github_api_request(
    *,
    token: str,
    method: str,
    path: str,
    params: dict[str, Any] | None = None,
    json_body: dict[str, Any] | None = None,
) -> Any:
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    url = f"{GITHUB_API_BASE}{path}"

    with httpx.Client(timeout=30.0) as client:
        response = client.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            json=json_body,
        )

    if response.status_code >= 400:
        detail = response.text
        raise RuntimeError(f"GitHub API error {response.status_code}: {detail}")

    return response.json()


def get_repo(token: str, owner: str, repo: str) -> dict[str, Any]:
    payload = _github_api_request(
        token=token,
        method="GET",
        path=f"/repos/{owner}/{repo}",
    )

    return {
        "id": payload.get("id"),
        "name": payload.get("name"),
        "full_name": payload.get("full_name"),
        "private": payload.get("private"),
        "default_branch": payload.get("default_branch"),
        "html_url": payload.get("html_url"),
        "description": payload.get("description"),
    }
