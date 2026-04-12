from __future__ import annotations

from typing import Any

import httpx

from .config import GITHUB_API_BASE
from .schemas import GitHubTokenData


class GitHubServiceError(Exception):
    def __init__(
        self,
        *,
        code: str,
        message: str,
        http_status: int | None = None,
        retryable: bool = False,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.http_status = http_status
        self.retryable = retryable
        self.details = details or {}


def get_token_data(oauth_token: GitHubTokenData | str) -> dict[str, Any]:
    if isinstance(oauth_token, str):
        return {
            "token": oauth_token,
            "scopes": [],
        }

    return {
        "token": oauth_token.get("token"),
        "scopes": oauth_token.get("scopes") or [],
    }


def _validate_required_scopes(
    granted_scopes: list[str], required_scopes: list[str]
) -> None:
    if not required_scopes:
        return

    if not granted_scopes:
        raise GitHubServiceError(
            code="MISSING_SCOPE",
            message="Token scopes are missing and required scopes cannot be verified.",
            http_status=403,
            details={
                "required_scopes": required_scopes,
                "granted_scopes": granted_scopes,
            },
        )

    missing = [scope for scope in required_scopes if scope not in granted_scopes]
    if missing:
        raise GitHubServiceError(
            code="MISSING_SCOPE",
            message="Token is missing required scopes.",
            http_status=403,
            details={
                "required_scopes": required_scopes,
                "granted_scopes": granted_scopes,
                "missing_scopes": missing,
            },
        )


def _github_api_request(
    *,
    oauth_token: GitHubTokenData | str,
    method: str,
    path: str,
    params: dict[str, Any] | None = None,
    json_body: dict[str, Any] | None = None,
    required_scopes: list[str] | None = None,
) -> Any:
    token_data = get_token_data(oauth_token)
    token = token_data.get("token")
    granted_scopes = token_data.get("scopes", [])

    if not token:
        raise GitHubServiceError(
            code="AUTH_MISSING",
            message="Missing token in oauth_token input.",
            http_status=401,
        )

    _validate_required_scopes(granted_scopes, required_scopes or [])

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
        if response.status_code == 401:
            raise GitHubServiceError(
                code="AUTH_INVALID",
                message="GitHub authentication failed.",
                http_status=401,
                details={"response": detail},
            )
        if response.status_code == 403:
            raise GitHubServiceError(
                code="FORBIDDEN",
                message="GitHub request forbidden for this token.",
                http_status=403,
                details={"response": detail},
            )
        if response.status_code == 404:
            raise GitHubServiceError(
                code="NOT_FOUND",
                message="Requested GitHub resource was not found.",
                http_status=404,
                details={"response": detail},
            )
        if response.status_code == 429:
            raise GitHubServiceError(
                code="RATE_LIMITED",
                message="GitHub API rate limit reached.",
                http_status=429,
                retryable=True,
                details={"response": detail},
            )

        raise GitHubServiceError(
            code="GITHUB_API_ERROR",
            message="GitHub API request failed.",
            http_status=response.status_code,
            details={"response": detail},
            retryable=response.status_code >= 500,
        )

    return response.json()


def get_repo(
    oauth_token: GitHubTokenData | str, owner: str, repo: str
) -> dict[str, Any]:
    payload = _github_api_request(
        oauth_token=oauth_token,
        method="GET",
        path=f"/repos/{owner}/{repo}",
        required_scopes=["repo"],
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


def list_branches(
    oauth_token: GitHubTokenData | str,
    owner: str,
    repo: str,
    page: int = 1,
    per_page: int = 30,
) -> list[dict[str, Any]]:
    payload = _github_api_request(
        oauth_token=oauth_token,
        method="GET",
        path=f"/repos/{owner}/{repo}/branches",
        params={"page": page, "per_page": per_page},
        required_scopes=["repo"],
    )

    # Mirror official minimal branch shaping: name, sha, protected
    result: list[dict[str, Any]] = []
    for branch in payload:
        result.append(
            {
                "name": branch.get("name"),
                "sha": (branch.get("commit") or {}).get("sha"),
                "protected": branch.get("protected", False),
            }
        )

    return result


def search_repositories(
    oauth_token: GitHubTokenData | str,
    query: str,
    sort: str = "stars",
    order: str = "desc",
    page: int = 1,
    per_page: int = 30,
) -> dict[str, Any]:
    """Search repositories with minimal output."""
    params = {
        "q": query,
        "sort": sort,
        "order": order,
        "page": page,
        "per_page": per_page,
    }

    payload = _github_api_request(
        oauth_token=oauth_token,
        method="GET",
        path="/search/repositories",
        params=params,
        required_scopes=["repo"],
    )

    result_items = []
    for item in payload.get("items", []):
        result_items.append(
            {
                "id": item.get("id"),
                "name": item.get("name"),
                "full_name": item.get("full_name"),
                "private": item.get("private"),
                "html_url": item.get("html_url"),
                "description": item.get("description"),
                "stars": item.get("stargazers_count"),
            }
        )

    return {
        "items": result_items,
        "total_count": payload.get("total_count", 0),
    }


def list_commits(
    oauth_token: GitHubTokenData | str,
    owner: str,
    repo: str,
    sha: str | None = None,
    path: str | None = None,
    author: str | None = None,
    since: str | None = None,
    until: str | None = None,
    page: int = 1,
    per_page: int = 30,
) -> list[dict[str, Any]]:
    """List commits for a repository with optional filters."""
    params = {
        "page": page,
        "per_page": per_page,
    }
    if sha:
        params["sha"] = sha
    if path:
        params["path"] = path
    if author:
        params["author"] = author
    if since:
        params["since"] = since
    if until:
        params["until"] = until

    payload = _github_api_request(
        oauth_token=oauth_token,
        method="GET",
        path=f"/repos/{owner}/{repo}/commits",
        params=params,
        required_scopes=["repo"],
    )

    result = []
    for commit in payload:
        author_info = commit.get("author") or {}
        committer_info = commit.get("committer") or {}
        commit_data = commit.get("commit") or {}

        result.append(
            {
                "sha": commit.get("sha"),
                "message": commit_data.get("message", ""),
                "author": {
                    "name": author_info.get("name"),
                    "email": author_info.get("email"),
                    "login": author_info.get("login"),
                },
                "committer": {
                    "name": committer_info.get("name"),
                    "email": committer_info.get("email"),
                    "login": committer_info.get("login"),
                },
                "date": commit_data.get("author", {}).get("date"),
            }
        )

    return result


def get_commit(
    oauth_token: GitHubTokenData | str,
    owner: str,
    repo: str,
    sha: str,
    include_diff: bool = True,
) -> dict[str, Any]:
    """Get details of a specific commit."""
    payload = _github_api_request(
        oauth_token=oauth_token,
        method="GET",
        path=f"/repos/{owner}/{repo}/commits/{sha}",
        required_scopes=["repo"],
    )

    author_info = payload.get("author") or {}
    committer_info = payload.get("committer") or {}
    commit_data = payload.get("commit") or {}

    result = {
        "sha": payload.get("sha"),
        "message": commit_data.get("message", ""),
        "author": {
            "name": author_info.get("name"),
            "email": author_info.get("email"),
            "login": author_info.get("login"),
        },
        "committer": {
            "name": committer_info.get("name"),
            "email": committer_info.get("email"),
            "login": committer_info.get("login"),
        },
        "date": commit_data.get("author", {}).get("date"),
        "url": payload.get("html_url"),
    }

    if include_diff:
        files = payload.get("files", [])
        result["files"] = [
            {
                "filename": f.get("filename"),
                "status": f.get("status"),
                "additions": f.get("additions"),
                "deletions": f.get("deletions"),
                "changes": f.get("changes"),
            }
            for f in files
        ]

    return result


def list_issues(
    oauth_token: GitHubTokenData | str,
    owner: str,
    repo: str,
    state: str = "open",
    labels: str | None = None,
    page: int = 1,
    per_page: int = 30,
) -> dict[str, Any]:
    """List issues for a repository."""
    params = {
        "state": state,
        "page": page,
        "per_page": per_page,
    }
    if labels:
        params["labels"] = labels

    payload = _github_api_request(
        oauth_token=oauth_token,
        method="GET",
        path=f"/repos/{owner}/{repo}/issues",
        params=params,
        required_scopes=["repo"],
    )

    issues = []
    for issue in payload:
        issues.append(
            {
                "number": issue.get("number"),
                "title": issue.get("title"),
                "state": issue.get("state"),
                "url": issue.get("html_url"),
                "body": issue.get("body"),
                "user": issue.get("user", {}).get("login"),
                "labels": [l.get("name") for l in issue.get("labels", [])],
                "created_at": issue.get("created_at"),
                "updated_at": issue.get("updated_at"),
            }
        )

    return {
        "issues": issues,
        "count": len(issues),
    }


def get_file_contents(
    oauth_token: GitHubTokenData | str,
    owner: str,
    repo: str,
    path: str = "/",
    ref: str | None = None,
) -> dict[str, Any]:
    """Get file or directory contents from a repository."""
    params = {}
    if ref:
        params["ref"] = ref

    payload = _github_api_request(
        oauth_token=oauth_token,
        method="GET",
        path=f"/repos/{owner}/{repo}/contents{path}",
        params=params,
        required_scopes=["repo"],
    )

    # Handle directory listing
    if isinstance(payload, list):
        items = []
        for item in payload:
            items.append(
                {
                    "name": item.get("name"),
                    "path": item.get("path"),
                    "type": item.get("type"),
                    "size": item.get("size"),
                    "url": item.get("html_url"),
                }
            )
        return {
            "type": "dir",
            "items": items,
        }

    # Handle single file
    return {
        "type": "file",
        "name": payload.get("name"),
        "path": payload.get("path"),
        "size": payload.get("size"),
        "url": payload.get("html_url"),
        "content": payload.get("content"),  # Base64 encoded if present
        "encoding": payload.get("encoding"),
    }


def list_org_repositories_by_contributor(
    oauth_token: GitHubTokenData | str,
    org: str,
    contributor_usernames: str | list[str],
    repo_type: str = "all",
) -> dict[str, Any]:
    """
    Find all repositories in an organization where specific users have contributed.
    Returns repos with filtered contributors and their individual contribution counts.

    Args:
        oauth_token: GitHub authentication token
        org: Organization name
        contributor_usernames: Single username (str) or list of usernames to filter by
        repo_type: Filter by repo type: "all", "public", or "private" (default: "all")
    """
    # Normalize input to list
    if isinstance(contributor_usernames, str):
        filter_usernames = [contributor_usernames]
    else:
        filter_usernames = contributor_usernames

    # Convert to set for faster lookup
    filter_set = set(username.lower() for username in filter_usernames)

    # Fetch all org repos (iterate through all pages)
    all_repos = []
    page = 1

    while True:
        params = {
            "type": repo_type,
            "page": page,
            "per_page": 100,  # Max allowed
        }

        org_repos_payload = _github_api_request(
            oauth_token=oauth_token,
            method="GET",
            path=f"/orgs/{org}/repos",
            params=params,
            required_scopes=["repo"],
        )

        if not org_repos_payload:
            break

        all_repos.extend(org_repos_payload)
        page += 1

    contributed_repos = []

    for repo in all_repos:
        repo_name = repo.get("name")
        repo_full_name = repo.get("full_name")

        # Get contributors for this repo
        try:
            contributors_payload = _github_api_request(
                oauth_token=oauth_token,
                method="GET",
                path=f"/repos/{repo_full_name}/contributors",
                params={"per_page": 100},
                required_scopes=["repo"],
            )

            # Find filtered contributors in this repo
            matching_contributors = []
            for contributor in contributors_payload:
                contributor_login = contributor.get("login", "").lower()
                if contributor_login in filter_set:
                    matching_contributors.append(
                        {
                            "username": contributor.get("login"),
                            "contributions": contributor.get("contributions", 0),
                        }
                    )

            # Only add repo if it has matching contributors
            if matching_contributors:
                contributed_repos.append(
                    {
                        "repo": repo_name,
                        "full_name": repo_full_name,
                        "url": repo.get("html_url"),
                        "private": repo.get("private", False),
                        "description": repo.get("description"),
                        "contributors": matching_contributors,
                        "total_filtered_contributions": sum(
                            c["contributions"] for c in matching_contributors
                        ),
                    }
                )

        except GitHubServiceError:
            # Skip repos where we can't access contributors (permission issues, etc.)
            continue

    return {
        "filter_contributors": filter_usernames,
        "organization": org,
        "repo_type_filter": repo_type,
        "total_repos_with_filtered_contributors": len(contributed_repos),
        "repos": contributed_repos,
    }
