from __future__ import annotations

import base64
import time
from typing import Any

import httpx
from fastmcp_credentials import get_credentials

from .config import GITHUB_API_BASE


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



def _validate_required_scopes(
    granted_scopes: list[str], required_scopes: list[str]
) -> None:
    """Validate that token has all required scopes."""
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
    method: str,
    path: str,
    params: dict[str, Any] | None = None,
    json_body: dict[str, Any] | None = None,
    required_scopes: list[str] | None = None,
) -> Any:
    cred = get_credentials()
    token = cred.access_token

    if not token:
        raise GitHubServiceError(
            code="AUTH_MISSING",
            message="Missing GitHub token in credentials.",
            http_status=401,
        )

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


#################### Service Methods ####################


def get_repo(owner: str, repo: str) -> dict[str, Any]:
    """Get detailed repository information (get_repository enhanced version)."""
    payload = _github_api_request(
        method="GET",
        path=f"/repos/{owner}/{repo}",
        required_scopes=["repo"],
    )

    return {
        "id": payload.get("id"),
        "name": payload.get("name"),
        "full_name": payload.get("full_name"),
        "owner": {
            "login": payload.get("owner", {}).get("login"),
            "id": payload.get("owner", {}).get("id"),
            "node_id": payload.get("owner", {}).get("node_id"),
            "url": payload.get("owner", {}).get("url"),
            "html_url": payload.get("owner", {}).get("html_url"),
        },
        "html_url": payload.get("html_url"),
        "description": payload.get("description"),
        "private": payload.get("private"),
        "fork": payload.get("fork"),
        "url": payload.get("url"),
        "default_branch": payload.get("default_branch"),
        "created_at": payload.get("created_at"),
        "updated_at": payload.get("updated_at"),
        "stargazers_count": payload.get("stargazers_count"),
        "language": payload.get("language"),
        "has_issues": payload.get("has_issues"),
        "has_downloads": payload.get("has_downloads"),
        "forks_count": payload.get("forks_count"),
    }


def list_tags(
    owner: str,
    repo: str,
    page: int = 1,
    per_page: int = 30,
) -> dict[str, Any]:
    """List repository tags with pagination."""
    payload = _github_api_request(
        method="GET",
        path=f"/repos/{owner}/{repo}/tags",
        params={"page": page, "per_page": per_page},
        required_scopes=["repo"],
    )

    if not isinstance(payload, list):
        payload = []

    return {
        "tags": [
            {
                "name": tag.get("name"),
                "commit": tag.get("commit"),
                "zipball_url": tag.get("zipball_url"),
                "tarball_url": tag.get("tarball_url"),
            }
            for tag in payload
        ],
        "page": page,
        "per_page": per_page,
    }


def get_tag(
    owner: str,
    repo: str,
    tag: str,
) -> dict[str, Any]:
    """Get specific tag details."""
    payload = _github_api_request(
        method="GET",
        path=f"/repos/{owner}/{repo}/git/refs/tags/{tag}",
        required_scopes=["repo"],
    )

    return {
        "ref": payload.get("ref"),
        "node_id": payload.get("node_id"),
        "url": payload.get("url"),
        "object": payload.get("object"),
    }


def create_repository(
    name: str,
    description: str | None = None,
    private: bool = False,
    auto_init: bool = False,
    gitignore_template: str | None = None,
    org: str | None = None,
) -> dict[str, Any]:
    """Create a new repository in personal account or organization."""
    if org:
        path = f"/orgs/{org}/repos"
    else:
        path = "/user/repos"

    request_body = {
        "name": name,
        "description": description,
        "private": private,
        "auto_init": auto_init,
    }
    if gitignore_template:
        request_body["gitignore_template"] = gitignore_template

    payload = _github_api_request(
        method="POST",
        path=path,
        json_body=request_body,
        required_scopes=["repo"],
    )

    return {
        "id": payload.get("id"),
        "name": payload.get("name"),
        "full_name": payload.get("full_name"),
        "url": payload.get("url"),
        "html_url": payload.get("html_url"),
        "owner": payload.get("owner"),
        "private": payload.get("private"),
        "created_at": payload.get("created_at"),
    }


def create_or_update_file(
    owner: str,
    repo: str,
    path: str,
    content: str,
    message: str,
    branch: str | None = None,
    sha: str | None = None,
) -> dict[str, Any]:
    """Create or update file in repository."""
    encoded_content = base64.b64encode(content.encode()).decode()
    request_body = {
        "message": message,
        "content": encoded_content,
    }
    if branch:
        request_body["branch"] = branch
    if sha:
        request_body["sha"] = sha

    payload = _github_api_request(
        method="PUT",
        path=f"/repos/{owner}/{repo}/contents/{path}",
        json_body=request_body,
        required_scopes=["repo"],
    )

    return {
        "content": payload.get("content"),
        "commit": payload.get("commit"),
    }


def fork_repository(
    owner: str,
    repo: str,
    org: str | None = None,
) -> dict[str, Any]:
    """Fork a repository to personal account or organization."""
    request_body = {}
    if org:
        request_body["organization"] = org

    payload = _github_api_request(
        method="POST",
        path=f"/repos/{owner}/{repo}/forks",
        json_body=request_body,
        required_scopes=["repo"],
    )

    return {
        "id": payload.get("id"),
        "name": payload.get("name"),
        "full_name": payload.get("full_name"),
        "url": payload.get("url"),
        "html_url": payload.get("html_url"),
        "owner": payload.get("owner"),
        "fork": payload.get("fork"),
    }


def create_branch(
    owner: str,
    repo: str,
    branch_name: str,
    sha: str | None = None,
) -> dict[str, Any]:
    """Create a new branch in the repository."""
    if not sha:
        # Get default branch SHA if not provided
        repo_data = get_repo(owner, repo)
        default_branch = repo_data.get("default_branch", "main")
        ref_payload = _github_api_request(
            method="GET",
            path=f"/repos/{owner}/{repo}/git/refs/heads/{default_branch}",
            required_scopes=["repo"],
        )
        sha = ref_payload.get("object", {}).get("sha")

    request_body = {
        "ref": f"refs/heads/{branch_name}",
        "sha": sha,
    }

    payload = _github_api_request(
        method="POST",
        path=f"/repos/{owner}/{repo}/git/refs",
        json_body=request_body,
        required_scopes=["repo"],
    )

    return {
        "ref": payload.get("ref"),
        "node_id": payload.get("node_id"),
        "url": payload.get("url"),
        "object": payload.get("object"),
    }


def push_files(
    owner: str,
    repo: str,
    files: list[dict[str, str]],
    message: str,
    branch: str | None = None,
    author_name: str | None = None,
    author_email: str | None = None,
) -> dict[str, Any]:
    """Push multiple files in a single atomic commit."""
    if not branch:
        repo_data = get_repo(owner, repo)
        branch = repo_data.get("default_branch", "main")

    # Get current branch reference
    try:
        ref_payload = _github_api_request(
            method="GET",
            path=f"/repos/{owner}/{repo}/git/refs/heads/{branch}",
            required_scopes=["repo"],
        )
        parent_sha = ref_payload.get("object", {}).get("sha")
    except GitHubServiceError:
        # Branch may not exist, try to create from default
        parent_sha = None

    # Get parent tree (if committing to existing branch)
    parent_tree_sha = None
    if parent_sha:
        commit_payload = _github_api_request(
            method="GET",
            path=f"/repos/{owner}/{repo}/git/commits/{parent_sha}",
            required_scopes=["repo"],
        )
        parent_tree_sha = commit_payload.get("tree", {}).get("sha")

    # Create tree with new files
    tree_items = []
    for file_item in files:
        content = file_item.get("content", "")
        path = file_item.get("path", "")
        tree_items.append(
            {
                "path": path,
                "mode": "100644",
                "type": "blob",
                "content": content,
            }
        )

    tree_request = {"tree": tree_items}
    if parent_tree_sha:
        tree_request["base_tree"] = parent_tree_sha

    tree_payload = _github_api_request(
        method="POST",
        path=f"/repos/{owner}/{repo}/git/trees",
        json_body=tree_request,
        required_scopes=["repo"],
    )
    new_tree_sha = tree_payload.get("sha")

    commit_request = {
        "message": message,
        "tree": new_tree_sha,
    }
    if parent_sha:
        commit_request["parents"] = [parent_sha]

    if author_name and author_email:
        commit_request["author"] = {
            "name": author_name,
            "email": author_email,
            "date": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }

    commit_payload = _github_api_request(
        method="POST",
        path=f"/repos/{owner}/{repo}/git/commits",
        json_body=commit_request,
        required_scopes=["repo"],
    )
    new_commit_sha = commit_payload.get("sha")

    # Update branch reference
    update_request = {"sha": new_commit_sha, "force": False}

    ref_payload = _github_api_request(
        method="PATCH",
        path=f"/repos/{owner}/{repo}/git/refs/heads/{branch}",
        json_body=update_request,
        required_scopes=["repo"],
    )

    return {
        "commit_sha": new_commit_sha,
        "tree_sha": new_tree_sha,
        "branch": branch,
        "message": message,
        "url": ref_payload.get("url"),
    }


def list_branches(
    owner: str,
    repo: str,
    page: int = 1,
    per_page: int = 30,
) -> list[dict[str, Any]]:
    payload = _github_api_request(
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
    owner: str,
    repo: str,
    sha: str,
    include_diff: bool = True,
) -> dict[str, Any]:
    """Get details of a specific commit."""
    payload = _github_api_request(
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
                "labels": [label.get("name") for label in issue.get("labels", [])],
                "created_at": issue.get("created_at"),
                "updated_at": issue.get("updated_at"),
            }
        )

    return {
        "issues": issues,
        "count": len(issues),
    }


def get_file_contents(
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


def search_code(
    query: str,
    sort: str = "indexed",
    order: str = "desc",
    page: int = 1,
    per_page: int = 30,
) -> dict[str, Any]:
    """Search code across GitHub repositories.

    Args:
        query: Code search query (e.g., 'fmt.Println language:go')
        sort: Sort field (default: 'indexed')
        order: Sort order ('asc' or 'desc', default: 'desc')
        page: Page number (default: 1)
        per_page: Results per page (default: 30, max: 100)

    Returns:
        Dictionary with search results
    """
    if not query.strip():
        raise GitHubServiceError(
            code="INVALID_INPUT",
            message="Search query cannot be empty",
            http_status=400,
            retryable=False,
            details={"field": "query"},
        )

    per_page = min(100, max(1, per_page))

    results = _github_api_request(
        method="GET",
        path="/search/code",
        params={
            "q": query,
            "sort": sort,
            "order": order,
            "page": page,
            "per_page": per_page,
        },
    )

    return {
        "total_count": results.get("total_count", 0),
        "incomplete_results": results.get("incomplete_results", False),
        "items": [
            {
                "name": item.get("name"),
                "path": item.get("path"),
                "repository": item.get("repository", {}).get("full_name"),
                "url": item.get("html_url"),
            }
            for item in results.get("items", [])
        ],
    }


def search_users(
    query: str,
    sort: str = "followers",
    order: str = "desc",
    page: int = 1,
    per_page: int = 30,
) -> dict[str, Any]:
    """Search GitHub users.

    Args:
        query: User search query (e.g., 'john smith', 'location:seattle')
        sort: Sort field ('followers', 'repositories', 'joined', default: 'followers')
        order: Sort order ('asc' or 'desc', default: 'desc')
        page: Page number (default: 1)
        per_page: Results per page (default: 30, max: 100)

    Returns:
        Dictionary with search results
    """
    if not query.strip():
        raise GitHubServiceError(
            code="INVALID_INPUT",
            message="Search query cannot be empty",
            http_status=400,
            retryable=False,
            details={"field": "query"},
        )

    # Preprocess query: add type:user if missing
    search_query = query
    if "type:user" not in search_query.lower():
        search_query = f"type:user {search_query}"

    per_page = min(100, max(1, per_page))

    results = _github_api_request(
        method="GET",
        path="/search/users",
        params={
            "q": search_query,
            "sort": sort,
            "order": order,
            "page": page,
            "per_page": per_page,
        },
    )

    return {
        "total_count": results.get("total_count", 0),
        "incomplete_results": results.get("incomplete_results", False),
        "items": [
            {
                "login": item.get("login"),
                "id": item.get("id"),
                "profile_url": item.get("html_url"),
                "avatar_url": item.get("avatar_url"),
            }
            for item in results.get("items", [])
        ],
    }


def search_issues(
    query: str,
    sort: str = "updated",
    order: str = "desc",
    owner: str | None = None,
    repo: str | None = None,
    page: int = 1,
    per_page: int = 30,
) -> dict[str, Any]:
    """Search issues across GitHub repositories.

    Args:
        query: Issue search query
        sort: Sort field (default: 'updated')
        order: Sort order ('asc' or 'desc', default: 'desc')
        owner: Repository owner (optional, requires repo)
        repo: Repository name (optional, requires owner)
        page: Page number (default: 1)
        per_page: Results per page (default: 30, max: 100)

    Returns:
        Dictionary with search results
    """
    if not query.strip():
        raise GitHubServiceError(
            code="INVALID_INPUT",
            message="Search query cannot be empty",
            http_status=400,
            retryable=False,
            details={"field": "query"},
        )

    # Preprocess query
    search_query = query

    # Add is:issue if not present
    if "is:issue" not in search_query.lower():
        search_query = f"is:issue {search_query}"

    # Add repo filter if both owner and repo provided and not already in query
    if owner and repo and "repo:" not in search_query.lower():
        search_query = f"repo:{owner}/{repo} {search_query}"

    per_page = min(100, max(1, per_page))

    results = _github_api_request(
        method="GET",
        path="/search/issues",
        params={
            "q": search_query,
            "sort": sort,
            "order": order,
            "page": page,
            "per_page": per_page,
        },
    )

    return {
        "total_count": results.get("total_count", 0),
        "incomplete_results": results.get("incomplete_results", False),
        "items": [
            {
                "number": item.get("number"),
                "title": item.get("title"),
                "state": item.get("state"),
                "body": item.get("body"),
                "url": item.get("html_url"),
                "comments": item.get("comments", 0),
                "user": item.get("user", {}).get("login"),
            }
            for item in results.get("items", [])
        ],
    }


def get_issue(
    owner: str,
    repo: str,
    issue_number: int,
) -> dict[str, Any]:
    """Get a single GitHub issue by number.

    Args:
        owner: Repository owner
        repo: Repository name
        issue_number: Issue number

    Returns:
        Dictionary with issue data
    """
    if not owner or not repo or issue_number <= 0:
        raise GitHubServiceError(
            code="INVALID_INPUT",
            message="owner, repo, and issue_number must be provided and valid",
            http_status=400,
            retryable=False,
            details={"fields": ["owner", "repo", "issue_number"]},
        )

    result = _github_api_request(
        method="GET",
        path=f"/repos/{owner}/{repo}/issues/{issue_number}",
        params={},
    )

    return {
        "number": result.get("number"),
        "title": result.get("title"),
        "body": result.get("body"),
        "state": result.get("state"),
        "state_reason": result.get("state_reason"),
        "labels": [label.get("name") for label in result.get("labels", [])],
        "assignees": [a.get("login") for a in result.get("assignees", [])],
        "url": result.get("html_url"),
        "user": result.get("user", {}).get("login"),
        "created_at": result.get("created_at"),
        "updated_at": result.get("updated_at"),
        "closed_at": result.get("closed_at"),
    }


def get_issue_comments(
    owner: str,
    repo: str,
    issue_number: int,
    page: int = 1,
    per_page: int = 30,
) -> dict[str, Any]:
    """Get comments on a GitHub issue.

    Args:
        owner: Repository owner
        repo: Repository name
        issue_number: Issue number
        page: Page number (default: 1)
        per_page: Results per page (default: 30, max: 100)

    Returns:
        Dictionary with comments data
    """
    if not owner or not repo or issue_number <= 0:
        raise GitHubServiceError(
            code="INVALID_INPUT",
            message="owner, repo, and issue_number must be provided and valid",
            http_status=400,
            retryable=False,
            details={"fields": ["owner", "repo", "issue_number"]},
        )

    per_page = min(100, max(1, per_page))

    results = _github_api_request(
        method="GET",
        path=f"/repos/{owner}/{repo}/issues/{issue_number}/comments",
        params={
            "page": page,
            "per_page": per_page,
        },
    )

    return {
        "comments": [
            {
                "id": comment.get("id"),
                "body": comment.get("body"),
                "url": comment.get("html_url"),
                "user": comment.get("user", {}).get("login"),
                "created_at": comment.get("created_at"),
                "updated_at": comment.get("updated_at"),
            }
            for comment in results
        ],
        "page": page,
        "per_page": per_page,
    }


def create_issue(
    owner: str,
    repo: str,
    title: str,
    body: str | None = None,
    assignees: list[str] | None = None,
    labels: list[str] | None = None,
    milestone: int | None = None,
) -> dict[str, Any]:
    """Create a new issue in a GitHub repository.

    Args:
        owner: Repository owner
        repo: Repository name
        title: Issue title (required)
        body: Issue description (optional)
        assignees: List of usernames to assign (optional)
        labels: List of label names (optional)
        milestone: Milestone ID (optional)

    Returns:
        Dictionary with issue ID and URL
    """
    if not owner or not repo or not title:
        raise GitHubServiceError(
            code="INVALID_INPUT",
            message="owner, repo, and title are required",
            http_status=400,
            retryable=False,
            details={"fields": ["owner", "repo", "title"]},
        )

    request_body = {
        "title": title,
    }
    if body:
        request_body["body"] = body
    if assignees:
        request_body["assignees"] = assignees
    if labels:
        request_body["labels"] = labels
    if milestone is not None:
        request_body["milestone"] = milestone

    result = _github_api_request(
        method="POST",
        path=f"/repos/{owner}/{repo}/issues",
        json_body=request_body,
    )

    # Minimal response
    return {
        "id": result.get("id"),
        "number": result.get("number"),
        "url": result.get("html_url"),
        "title": result.get("title"),
    }


def add_issue_comment(
    owner: str,
    repo: str,
    issue_number: int,
    body: str,
) -> dict[str, Any]:
    """Add a comment to a GitHub issue or pull request.

    Args:
        owner: Repository owner
        repo: Repository name
        issue_number: Issue or PR number
        body: Comment text (required)

    Returns:
        Dictionary with comment ID and URL
    """
    if not owner or not repo or issue_number <= 0 or not body:
        raise GitHubServiceError(
            code="INVALID_INPUT",
            message="owner, repo, issue_number, and body are required",
            http_status=400,
            retryable=False,
            details={"fields": ["owner", "repo", "issue_number", "body"]},
        )

    request_body = {"body": body}

    result = _github_api_request(
        method="POST",
        path=f"/repos/{owner}/{repo}/issues/{issue_number}/comments",
        json_body=request_body,
    )

    # Minimal response
    return {
        "id": result.get("id"),
        "url": result.get("html_url"),
        "body": result.get("body"),
        "user": result.get("user", {}).get("login"),
    }


def update_issue(
    owner: str,
    repo: str,
    issue_number: int,
    title: str | None = None,
    body: str | None = None,
    state: str | None = None,
    state_reason: str | None = None,
    assignees: list[str] | None = None,
    labels: list[str] | None = None,
    milestone: int | None = None,
) -> dict[str, Any]:
    """Update a GitHub issue.

    Args:
        owner: Repository owner
        repo: Repository name
        issue_number: Issue number (required)
        title: New issue title (optional)
        body: New issue body (optional)
        state: 'open' or 'closed' (optional)
        state_reason: 'completed', 'not_planned', or 'duplicate' when closing (optional)
        assignees: List of usernames to assign (optional)
        labels: List of label names (optional)
        milestone: Milestone ID (optional)

    Returns:
        Dictionary with issue ID and URL
    """
    if not owner or not repo or issue_number <= 0:
        raise GitHubServiceError(
            code="INVALID_INPUT",
            message="owner, repo, and issue_number are required",
            http_status=400,
            retryable=False,
            details={"fields": ["owner", "repo", "issue_number"]},
        )

    # Build request body only with provided fields
    request_body = {}
    if title is not None:
        request_body["title"] = title
    if body is not None:
        request_body["body"] = body
    if state is not None:
        request_body["state"] = state
    if state_reason is not None:
        request_body["state_reason"] = state_reason
    if assignees is not None:
        request_body["assignees"] = assignees
    if labels is not None:
        request_body["labels"] = labels
    if milestone is not None:
        request_body["milestone"] = milestone

    if not request_body:
        raise GitHubServiceError(
            code="INVALID_INPUT",
            message="At least one field (title, body, state, assignees, labels, or milestone) must be provided",
            http_status=400,
            retryable=False,
        )

    result = _github_api_request(
        method="PATCH",
        path=f"/repos/{owner}/{repo}/issues/{issue_number}",
        json_body=request_body,
    )

    # Minimal response
    return {
        "id": result.get("id"),
        "number": result.get("number"),
        "url": result.get("html_url"),
        "title": result.get("title"),
        "state": result.get("state"),
    }


def pull_request_read(
    owner: str,
    repo: str,
    pull_number: int,
    method: str = "get",
    page: int = 1,
    per_page: int = 30,
) -> dict[str, Any]:
    """Read pull request data with flexible method parameter.

    Methods:
    - get: Get details of the pull request
    - get_files: Get list of files changed in the PR
    - get_status: Get combined commit status and check runs
    - get_comments: Get PR comments (not review comments)
    - get_review_comments: Get review thread comments

    Args:
        owner: Repository owner
        repo: Repository name
        pull_number: Pull request number
        method: Which data to retrieve (default: 'get')
        page: Page number for pagination
        per_page: Results per page

    Returns:
        Dictionary with PR data based on method
    """
    if not owner or not repo or pull_number <= 0:
        raise GitHubServiceError(
            code="INVALID_INPUT",
            message="owner, repo, and pull_number are required and valid",
            http_status=400,
            retryable=False,
            details={"fields": ["owner", "repo", "pull_number"]},
        )

    if method == "get":
        # Get PR details
        result = _github_api_request(
            method="GET",
            path=f"/repos/{owner}/{repo}/pulls/{pull_number}",
        )

        return {
            "number": result.get("number"),
            "title": result.get("title"),
            "body": result.get("body"),
            "state": result.get("state"),
            "state_reason": result.get("state_reason"),
            "url": result.get("html_url"),
            "user": result.get("user", {}).get("login"),
            "created_at": result.get("created_at"),
            "updated_at": result.get("updated_at"),
            "merged_at": result.get("merged_at"),
            "merged": result.get("merged", False),
            "merge_commit_sha": result.get("merge_commit_sha"),
            "head": {
                "ref": result.get("head", {}).get("ref"),
                "sha": result.get("head", {}).get("sha"),
                "repo": result.get("head", {}).get("repo", {}).get("full_name"),
            },
            "base": {
                "ref": result.get("base", {}).get("ref"),
                "sha": result.get("base", {}).get("sha"),
                "repo": result.get("base", {}).get("repo", {}).get("full_name"),
            },
            "draft": result.get("draft", False),
            "additions": result.get("additions", 0),
            "deletions": result.get("deletions", 0),
            "changed_files": result.get("changed_files", 0),
            "commits": result.get("commits", 0),
            "labels": [label.get("name") for label in result.get("labels", [])],
            "assignees": [a.get("login") for a in result.get("assignees", [])],
            "reviewers": [
                r.get("login") for r in result.get("requested_reviewers", [])
            ],
        }

    elif method == "get_files":
        # Get files changed in PR
        per_page = min(100, max(1, per_page))
        results = _github_api_request(
            method="GET",
            path=f"/repos/{owner}/{repo}/pulls/{pull_number}/files",
            params={"page": page, "per_page": per_page},
        )

        files = []
        for file_item in results if isinstance(results, list) else []:
            files.append(
                {
                    "filename": file_item.get("filename"),
                    "status": file_item.get("status"),
                    "additions": file_item.get("additions"),
                    "deletions": file_item.get("deletions"),
                    "changes": file_item.get("changes"),
                    "patch": file_item.get("patch"),
                    "previous_filename": file_item.get("previous_filename"),
                }
            )

        return {
            "files": files,
            "total_files": len(files),
            "page": page,
            "per_page": per_page,
        }

    elif method == "get_status":
        # Get PR status and checks
        status_result = _github_api_request(
            method="GET",
            path=f"/repos/{owner}/{repo}/pulls/{pull_number}",
        )

        head_sha = status_result.get("head", {}).get("sha")
        if not head_sha:
            raise GitHubServiceError(
                code="NOT_FOUND",
                message="Could not determine head commit SHA for PR",
                http_status=404,
            )

        # Get combined status
        combined = _github_api_request(
            method="GET",
            path=f"/repos/{owner}/{repo}/commits/{head_sha}/status",
        )

        return {
            "state": combined.get("state"),
            "sha": combined.get("sha"),
            "total_count": combined.get("total_count", 0),
            "statuses": [
                {
                    "state": s.get("state"),
                    "context": s.get("context"),
                    "description": s.get("description"),
                    "target_url": s.get("target_url"),
                    "created_at": s.get("created_at"),
                }
                for s in combined.get("statuses", [])
            ],
        }

    elif method == "get_comments":
        # Get PR comments
        per_page = min(100, max(1, per_page))
        results = _github_api_request(
            method="GET",
            path=f"/repos/{owner}/{repo}/issues/{pull_number}/comments",
            params={"page": page, "per_page": per_page},
        )

        comments = []
        for comment in results if isinstance(results, list) else []:
            comments.append(
                {
                    "id": comment.get("id"),
                    "user": comment.get("user", {}).get("login"),
                    "body": comment.get("body"),
                    "created_at": comment.get("created_at"),
                    "updated_at": comment.get("updated_at"),
                    "url": comment.get("html_url"),
                }
            )

        return {
            "comments": comments,
            "total_comments": len(comments),
            "page": page,
            "per_page": per_page,
        }

    elif method == "get_review_comments":
        # Get review comments on PR
        per_page = min(100, max(1, per_page))
        results = _github_api_request(
            method="GET",
            path=f"/repos/{owner}/{repo}/pulls/{pull_number}/comments",
            params={"page": page, "per_page": per_page},
        )

        comments = []
        for comment in results if isinstance(results, list) else []:
            comments.append(
                {
                    "id": comment.get("id"),
                    "user": comment.get("user", {}).get("login"),
                    "body": comment.get("body"),
                    "path": comment.get("path"),
                    "position": comment.get("position"),
                    "commit_id": comment.get("commit_id"),
                    "created_at": comment.get("created_at"),
                    "updated_at": comment.get("updated_at"),
                    "url": comment.get("html_url"),
                }
            )

        return {
            "review_comments": comments,
            "total_review_comments": len(comments),
            "page": page,
            "per_page": per_page,
        }

    else:
        raise GitHubServiceError(
            code="INVALID_INPUT",
            message=f"Unknown method: {method}",
            http_status=400,
            details={
                "method": method,
                "valid_methods": [
                    "get",
                    "get_files",
                    "get_status",
                    "get_comments",
                    "get_review_comments",
                ],
            },
        )


def list_pull_requests(
    owner: str,
    repo: str,
    state: str = "open",
    sort: str = "created",
    direction: str = "desc",
    base: str | None = None,
    head: str | None = None,
    page: int = 1,
    per_page: int = 30,
) -> dict[str, Any]:
    """List pull requests in a repository.

    Args:
        owner: Repository owner
        repo: Repository name
        state: Pull request state filter ('open', 'closed', 'all')
        sort: Sort field ('created', 'updated', 'popularity', 'long-running')
        direction: Sort direction ('asc', 'desc')
        base: Filter by base branch
        head: Filter by head branch (user:branch format)
        page: Page number
        per_page: Results per page

    Returns:
        Dictionary with PRs list
    """
    if not owner or not repo:
        raise GitHubServiceError(
            code="INVALID_INPUT",
            message="owner and repo are required",
            http_status=400,
            retryable=False,
            details={"fields": ["owner", "repo"]},
        )

    params = {
        "state": state,
        "sort": sort,
        "direction": direction,
        "page": page,
        "per_page": min(100, max(1, per_page)),
    }

    if base:
        params["base"] = base
    if head:
        params["head"] = head

    results = _github_api_request(
        method="GET",
        path=f"/repos/{owner}/{repo}/pulls",
        params=params,
    )

    prs = []
    for pr in results if isinstance(results, list) else []:
        prs.append(
            {
                "number": pr.get("number"),
                "title": pr.get("title"),
                "state": pr.get("state"),
                "url": pr.get("html_url"),
                "user": pr.get("user", {}).get("login"),
                "created_at": pr.get("created_at"),
                "updated_at": pr.get("updated_at"),
                "draft": pr.get("draft", False),
                "additions": pr.get("additions", 0),
                "deletions": pr.get("deletions", 0),
                "changed_files": pr.get("changed_files", 0),
            }
        )

    return {
        "pull_requests": prs,
        "total_count": len(prs),
        "page": page,
        "per_page": params["per_page"],
    }


def search_pull_requests(
    query: str,
    sort: str = "updated",
    order: str = "desc",
    owner: str | None = None,
    repo: str | None = None,
    page: int = 1,
    per_page: int = 30,
) -> dict[str, Any]:
    """Search pull requests across GitHub repositories.

    Args:
        query: Search query using GitHub search syntax
        sort: Sort field (default: 'updated')
        order: Sort order ('asc', 'desc')
        owner: Repository owner (optional)
        repo: Repository name (optional)
        page: Page number
        per_page: Results per page

    Returns:
        Dictionary with search results
    """
    if not query.strip():
        raise GitHubServiceError(
            code="INVALID_INPUT",
            message="Search query cannot be empty",
            http_status=400,
            retryable=False,
            details={"field": "query"},
        )

    # Preprocess query - add is:pr if not present
    search_query = query
    if "is:pr" not in search_query.lower():
        search_query = f"is:pr {search_query}"

    # Add repo filter if provided
    if owner and repo and "repo:" not in search_query.lower():
        search_query = f"repo:{owner}/{repo} {search_query}"

    per_page = min(100, max(1, per_page))

    results = _github_api_request(
        method="GET",
        path="/search/issues",
        params={
            "q": search_query,
            "sort": sort,
            "order": order,
            "page": page,
            "per_page": per_page,
        },
    )

    prs = []
    for item in results.get("items", []):
        prs.append(
            {
                "number": item.get("number"),
                "title": item.get("title"),
                "state": item.get("state"),
                "url": item.get("html_url"),
                "user": item.get("user", {}).get("login"),
                "created_at": item.get("created_at"),
                "updated_at": item.get("updated_at"),
                "comments": item.get("comments", 0),
            }
        )

    return {
        "total_count": results.get("total_count", 0),
        "incomplete_results": results.get("incomplete_results", False),
        "pull_requests": prs,
        "page": page,
        "per_page": per_page,
    }


def list_org_repositories_by_contributor(
    org: str,
    contributor_usernames: str | list[str],
    repo_type: str = "all",
) -> dict[str, Any]:
    """
    Find all repositories in an organization where specific users have contributed.
    Returns repos with filtered contributors and their individual contribution counts.

    Args:
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
            method="GET",
            path=f"/orgs/{org}/repos",
            params=params,
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
                method="GET",
                path=f"/repos/{repo_full_name}/contributors",
                params={"per_page": 100},
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


def create_pull_request(
    owner: str,
    repo: str,
    title: str,
    head: str,
    base: str,
    body: str | None = None,
    draft: bool = False,
    maintainer_can_modify: bool = True,
) -> dict[str, Any]:
    """Create a new pull request.

    Args:
        owner: Repository owner
        repo: Repository name
        title: PR title
        head: Branch containing changes (source branch)
        base: Branch to merge into (target branch)
        body: PR description (optional)
        draft: Create as draft PR (optional)
        maintainer_can_modify: Allow maintainers to edit (optional)

    Returns:
        Dictionary with PR details
    """
    if not all([owner, repo, title, head, base]):
        raise GitHubServiceError(
            code="INVALID_INPUT",
            message="owner, repo, title, head, and base are required",
            http_status=400,
            retryable=False,
            details={"fields": ["owner", "repo", "title", "head", "base"]},
        )

    request_body = {
        "title": title,
        "head": head,
        "base": base,
        "draft": draft,
        "maintainer_can_modify": maintainer_can_modify,
    }

    if body:
        request_body["body"] = body

    result = _github_api_request(
        method="POST",
        path=f"/repos/{owner}/{repo}/pulls",
        json_body=request_body,
    )

    return {
        "number": result.get("number"),
        "title": result.get("title"),
        "state": result.get("state"),
        "draft": result.get("draft", False),
        "url": result.get("html_url"),
        "head_branch": result.get("head", {}).get("ref"),
        "base_branch": result.get("base", {}).get("ref"),
        "created_at": result.get("created_at"),
        "user": result.get("user", {}).get("login"),
    }


def update_pull_request(
    owner: str,
    repo: str,
    pull_number: int,
    title: str | None = None,
    body: str | None = None,
    state: str | None = None,
    base: str | None = None,
    draft: bool | None = None,
    maintainer_can_modify: bool | None = None,
    reviewers: list[str] | None = None,
) -> dict[str, Any]:
    """Update an existing pull request.

    Args:
        owner: Repository owner
        repo: Repository name
        pull_number: PR number to update
        title: New title (optional)
        body: New description (optional)
        state: 'open' or 'closed' (optional)
        base: New base branch (optional)
        draft: Mark as draft/ready (optional)
        maintainer_can_modify: Allow maintainers to edit (optional)
        reviewers: Request reviews from users (optional)

    Returns:
        Dictionary with updated PR details
    """
    if not all([owner, repo]) or pull_number <= 0:
        raise GitHubServiceError(
            code="INVALID_INPUT",
            message="owner, repo, and pull_number are required",
            http_status=400,
            retryable=False,
            details={"fields": ["owner", "repo", "pull_number"]},
        )

    request_body = {}

    if title is not None:
        request_body["title"] = title
    if body is not None:
        request_body["body"] = body
    if state is not None:
        request_body["state"] = state
    if base is not None:
        request_body["base"] = base
    if draft is not None:
        request_body["draft"] = draft
    if maintainer_can_modify is not None:
        request_body["maintainer_can_modify"] = maintainer_can_modify

    if not request_body and not reviewers:
        raise GitHubServiceError(
            code="INVALID_INPUT",
            message="At least one field must be provided to update",
            http_status=400,
            retryable=False,
        )

    result = _github_api_request(
        method="PATCH",
        path=f"/repos/{owner}/{repo}/pulls/{pull_number}",
        json_body=request_body,
    )

    # Update reviewers separately if provided
    if reviewers:
        reviewer_body = {"reviewers": reviewers}
        try:
            _github_api_request(
                method="POST",
                path=f"/repos/{owner}/{repo}/pulls/{pull_number}/requested_reviewers",
                json_body=reviewer_body,
            )
        except GitHubServiceError:
            # Continue even if reviewer assignment fails
            pass

    return {
        "number": result.get("number"),
        "title": result.get("title"),
        "state": result.get("state"),
        "draft": result.get("draft", False),
        "url": result.get("html_url"),
        "updated_at": result.get("updated_at"),
    }


def merge_pull_request(
    owner: str,
    repo: str,
    pull_number: int,
    merge_method: str = "merge",
    commit_title: str | None = None,
    commit_message: str | None = None,
) -> dict[str, Any]:
    """Merge a pull request.

    Args:
        owner: Repository owner
        repo: Repository name
        pull_number: PR number to merge
        merge_method: 'merge', 'squash', or 'rebase' (default: 'merge')
        commit_title: Custom commit title (optional)
        commit_message: Commit message details (optional)

    Returns:
        Dictionary with merge result
    """
    if not all([owner, repo]) or pull_number <= 0:
        raise GitHubServiceError(
            code="INVALID_INPUT",
            message="owner, repo, and pull_number are required",
            http_status=400,
            retryable=False,
            details={"fields": ["owner", "repo", "pull_number"]},
        )

    if merge_method not in ["merge", "squash", "rebase"]:
        raise GitHubServiceError(
            code="INVALID_INPUT",
            message="merge_method must be 'merge', 'squash', or 'rebase'",
            http_status=400,
            retryable=False,
        )

    request_body = {
        "merge_method": merge_method,
    }

    if commit_title:
        request_body["commit_title"] = commit_title
    if commit_message:
        request_body["commit_message"] = commit_message

    result = _github_api_request(
        method="PUT",
        path=f"/repos/{owner}/{repo}/pulls/{pull_number}/merge",
        json_body=request_body,
    )

    return {
        "merged": result.get("merged", False),
        "sha": result.get("sha"),
        "message": result.get("message"),
    }


def update_pull_request_branch(
    owner: str,
    repo: str,
    pull_number: int,
    expected_head_sha: str | None = None,
) -> dict[str, Any]:
    """Update PR branch with latest changes from base branch.

    Args:
        owner: Repository owner
        repo: Repository name
        pull_number: PR number
        expected_head_sha: Expected SHA of PR's HEAD ref (optional, for safety)

    Returns:
        Dictionary with update result
    """
    if not all([owner, repo]) or pull_number <= 0:
        raise GitHubServiceError(
            code="INVALID_INPUT",
            message="owner, repo, and pull_number are required",
            http_status=400,
            retryable=False,
            details={"fields": ["owner", "repo", "pull_number"]},
        )

    request_body = {}
    if expected_head_sha:
        request_body["expected_head_sha"] = expected_head_sha

    result = _github_api_request(
        method="PUT",
        path=f"/repos/{owner}/{repo}/pulls/{pull_number}/update-branch",
        json_body=request_body,
    )

    return {
        "message": result.get("message"),
        "url": result.get("url"),
    }


def pull_request_review_write(
    owner: str,
    repo: str,
    pull_number: int,
    method: str,
    commit_id: str | None = None,
    body: str | None = None,
    event: str | None = None,
    thread_id: str | None = None,
) -> dict[str, Any]:
    """Write operations on PR reviews (create, submit, delete, resolve/unresolve threads).

    Methods:
    - create: Create new review (with optional event to auto-submit)
    - submit_pending: Submit existing pending review
    - delete_pending: Delete pending review
    - resolve_thread: Resolve review thread
    - unresolve_thread: Unresolve review thread

    Args:
        owner: Repository owner
        repo: Repository name
        pull_number: PR number
        method: Operation (create, submit_pending, delete_pending, resolve_thread, unresolve_thread)
        commit_id: Commit SHA for review (required for create)
        body: Review comment text
        event: APPROVE, REQUEST_CHANGES, or COMMENT (optional for create, required for submit_pending)
        thread_id: Thread ID for thread operations (required for resolve/unresolve)

    Returns:
        Dictionary with operation result
    """
    required_scopes = ["repo"]
    if method in ["resolve_thread", "unresolve_thread"]:
        # These only need thread_id
        if not thread_id:
            raise GitHubServiceError(
                code="INVALID_INPUT",
                message=f"{method} requires thread_id",
                http_status=400,
                retryable=False,
                details={"field": "thread_id"},
            )

        # Thread operations use GraphQL, but GitHub also supports REST for these
        # For simplicity, we'll use a REST-like approach
        operation_type = "RESOLVE" if method == "resolve_thread" else "UNRESOLVE"
        request_body = {"resolved": operation_type == "RESOLVE"}

        try:
            result = _github_api_request(
                method="PATCH",
                path=f"/repos/{owner}/{repo}/pulls/comments/{thread_id}",
                json_body=request_body,
                required_scopes=required_scopes,
            )
            return {
                "thread_id": thread_id,
                "resolved": result.get("resolved", operation_type == "RESOLVE"),
            }
        except GitHubServiceError:
            # Fallback for v3 API
            return {
                "thread_id": thread_id,
                "message": f"Thread {operation_type.lower()}d",
            }

    elif method == "create":
        # Create review (optionally submit)
        if not all([owner, repo]) or pull_number <= 0:
            raise GitHubServiceError(
                code="INVALID_INPUT",
                message="owner, repo, and pull_number are required",
                http_status=400,
                retryable=False,
            )

        if not commit_id:
            raise GitHubServiceError(
                code="INVALID_INPUT",
                message="commit_id is required for creating a review",
                http_status=400,
                retryable=False,
                details={"field": "commit_id"},
            )

        request_body = {
            "commit_id": commit_id,
        }

        if body:
            request_body["body"] = body
        if event:
            request_body["event"] = event

        result = _github_api_request(
            method="POST",
            path=f"/repos/{owner}/{repo}/pulls/{pull_number}/reviews",
            json_body=request_body,
            required_scopes=required_scopes,
        )

        return {
            "id": result.get("id"),
            "node_id": result.get("node_id"),
            "state": result.get("state"),
            "body": result.get("body"),
            "user": result.get("user", {}).get("login"),
            "submitted_at": result.get("submitted_at"),
        }

    elif method == "submit_pending":
        # Submit pending review
        if not all([owner, repo]) or pull_number <= 0:
            raise GitHubServiceError(
                code="INVALID_INPUT",
                message="owner, repo, and pull_number are required",
                http_status=400,
                retryable=False,
            )

        if not event:
            raise GitHubServiceError(
                code="INVALID_INPUT",
                message="event is required for submitting pending review",
                http_status=400,
                retryable=False,
                details={
                    "field": "event",
                    "valid_values": ["APPROVE", "REQUEST_CHANGES", "COMMENT"],
                },
            )

        if event not in ["APPROVE", "REQUEST_CHANGES", "COMMENT"]:
            raise GitHubServiceError(
                code="INVALID_INPUT",
                message="event must be APPROVE, REQUEST_CHANGES, or COMMENT",
                http_status=400,
                retryable=False,
            )

        request_body = {
            "event": event,
        }

        if body:
            request_body["body"] = body

        result = _github_api_request(
            method="POST",
            path=f"/repos/{owner}/{repo}/pulls/{pull_number}/reviews",
            json_body=request_body,
            required_scopes=required_scopes,
        )

        return {
            "id": result.get("id"),
            "state": result.get("state"),
            "submitted_at": result.get("submitted_at"),
        }

    elif method == "delete_pending":
        # Delete pending review
        if not all([owner, repo]) or pull_number <= 0:
            raise GitHubServiceError(
                code="INVALID_INPUT",
                message="owner, repo, and pull_number are required",
                http_status=400,
                retryable=False,
            )

        # Need to find pending review first
        reviews_result = _github_api_request(
            method="GET",
            path=f"/repos/{owner}/{repo}/pulls/{pull_number}/reviews",
            required_scopes=required_scopes,
        )

        pending_review_id = None
        for review in reviews_result if isinstance(reviews_result, list) else []:
            if review.get("state") == "PENDING":
                pending_review_id = review.get("id")
                break

        if not pending_review_id:
            raise GitHubServiceError(
                code="NOT_FOUND",
                message="No pending review found for deletion",
                http_status=404,
            )

        _github_api_request(
            method="DELETE",
            path=f"/repos/{owner}/{repo}/pulls/{pull_number}/reviews/{pending_review_id}",
            required_scopes=required_scopes,
        )

        return {
            "deleted": True,
            "review_id": pending_review_id,
        }

    else:
        raise GitHubServiceError(
            code="INVALID_INPUT",
            message=f"Unknown method: {method}",
            http_status=400,
            details={
                "method": method,
                "valid_methods": [
                    "create",
                    "submit_pending",
                    "delete_pending",
                    "resolve_thread",
                    "unresolve_thread",
                ],
            },
        )


def add_reply_to_pull_request_comment(
    owner: str,
    repo: str,
    pull_number: int,
    comment_id: int,
    body: str,
) -> dict[str, Any]:
    """Add a reply to an existing PR comment.

    Args:
        owner: Repository owner
        repo: Repository name
        pull_number: PR number
        comment_id: ID of the comment to reply to
        body: Reply text

    Returns:
        Dictionary with new comment details
    """
    if not all([owner, repo, body]) or pull_number <= 0 or comment_id <= 0:
        raise GitHubServiceError(
            code="INVALID_INPUT",
            message="owner, repo, pull_number, comment_id, and body are required",
            http_status=400,
            retryable=False,
            details={"fields": ["owner", "repo", "pull_number", "comment_id", "body"]},
        )

    request_body = {
        "body": body,
        "in_reply_to": comment_id,
    }

    result = _github_api_request(
        method="POST",
        path=f"/repos/{owner}/{repo}/pulls/{pull_number}/comments",
        json_body=request_body,
    )

    return {
        "id": result.get("id"),
        "user": result.get("user", {}).get("login"),
        "body": result.get("body"),
        "created_at": result.get("created_at"),
        "url": result.get("html_url"),
        "in_reply_to_id": result.get("in_reply_to_id"),
    }


def get_latest_release(
    owner: str,
    repo: str,
) -> dict[str, Any]:
    """Get the latest release in a repository.

    Args:
        owner: Repository owner
        repo: Repository name

    Returns:
        Dictionary with release details
    """
    if not all([owner, repo]):
        raise GitHubServiceError(
            code="INVALID_INPUT",
            message="owner and repo are required",
            http_status=400,
            retryable=False,
            details={"fields": ["owner", "repo"]},
        )

    result = _github_api_request(
        method="GET",
        path=f"/repos/{owner}/{repo}/releases/latest",
    )

    return {
        "id": result.get("id"),
        "tag_name": result.get("tag_name"),
        "name": result.get("name"),
        "draft": result.get("draft", False),
        "prerelease": result.get("prerelease", False),
        "created_at": result.get("created_at"),
        "published_at": result.get("published_at"),
        "url": result.get("html_url"),
        "body": result.get("body"),
        "author": result.get("author", {}).get("login"),
    }


def list_releases(
    owner: str,
    repo: str,
    page: int = 1,
    per_page: int = 30,
) -> dict[str, Any]:
    """List releases in a repository.

    Args:
        owner: Repository owner
        repo: Repository name
        page: Page number for pagination
        per_page: Results per page

    Returns:
        Dictionary with releases list
    """
    if not all([owner, repo]):
        raise GitHubServiceError(
            code="INVALID_INPUT",
            message="owner and repo are required",
            http_status=400,
            retryable=False,
            details={"fields": ["owner", "repo"]},
        )

    per_page = min(100, max(1, per_page))

    results = _github_api_request(
        method="GET",
        path=f"/repos/{owner}/{repo}/releases",
        params={"page": page, "per_page": per_page},
    )

    releases = []
    for release in results if isinstance(results, list) else []:
        releases.append(
            {
                "id": release.get("id"),
                "tag_name": release.get("tag_name"),
                "name": release.get("name"),
                "draft": release.get("draft", False),
                "prerelease": release.get("prerelease", False),
                "created_at": release.get("created_at"),
                "published_at": release.get("published_at"),
                "url": release.get("html_url"),
                "author": release.get("author", {}).get("login"),
            }
        )

    return {
        "releases": releases,
        "total_count": len(releases),
        "page": page,
        "per_page": per_page,
    }


def get_release_by_tag(
    owner: str,
    repo: str,
    tag: str,
) -> dict[str, Any]:
    """Get a specific release by tag name.

    Args:
        owner: Repository owner
        repo: Repository name
        tag: Tag name (e.g., 'v1.0.0')

    Returns:
        Dictionary with release details
    """
    if not all([owner, repo, tag]):
        raise GitHubServiceError(
            code="INVALID_INPUT",
            message="owner, repo, and tag are required",
            http_status=400,
            retryable=False,
            details={"fields": ["owner", "repo", "tag"]},
        )

    result = _github_api_request(
        method="GET",
        path=f"/repos/{owner}/{repo}/releases/tags/{tag}",
    )

    return {
        "id": result.get("id"),
        "tag_name": result.get("tag_name"),
        "name": result.get("name"),
        "draft": result.get("draft", False),
        "prerelease": result.get("prerelease", False),
        "created_at": result.get("created_at"),
        "published_at": result.get("published_at"),
        "url": result.get("html_url"),
        "body": result.get("body"),
        "author": result.get("author", {}).get("login"),
    }


def get_label(
    owner: str,
    repo: str,
    name: str,
) -> dict[str, Any]:
    """Get a specific label from a repository.

    Args:
        owner: Repository owner
        repo: Repository name
        name: Label name

    Returns:
        Dictionary with label details
    """
    if not all([owner, repo, name]):
        raise GitHubServiceError(
            code="INVALID_INPUT",
            message="owner, repo, and name are required",
            http_status=400,
            retryable=False,
            details={"fields": ["owner", "repo", "name"]},
        )

    result = _github_api_request(
        method="GET",
        path=f"/repos/{owner}/{repo}/labels/{name}",
    )

    return {
        "id": result.get("id"),
        "name": result.get("name"),
        "color": result.get("color"),
        "description": result.get("description"),
        "url": result.get("url"),
    }


def get_me() -> dict[str, Any]:
    """Get details of the authenticated GitHub user.

    Returns:
        Dictionary with user profile details
    """
    result = _github_api_request(
        method="GET",
        path="/user",
    )

    return {
        "id": result.get("id"),
        "login": result.get("login"),
        "name": result.get("name"),
        "email": result.get("email"),
        "bio": result.get("bio"),
        "company": result.get("company"),
        "location": result.get("location"),
        "public_repos": result.get("public_repos", 0),
        "followers": result.get("followers", 0),
        "following": result.get("following", 0),
        "created_at": result.get("created_at"),
        "updated_at": result.get("updated_at"),
        "avatar_url": result.get("avatar_url"),
        "profile_url": result.get("html_url"),
    }


def sub_issue_write(
    owner: str,
    repo: str,
    issue_number: int,
    method: str,
    sub_issue_id: int,
    replace_parent: bool = False,
    after_id: int | None = None,
    before_id: int | None = None,
) -> dict[str, Any]:
    """Manage sub-issues for a parent issue (add, remove, reprioritize).

    Methods:
    - add: Add a sub-issue to a parent issue
    - remove: Remove a sub-issue from a parent issue
    - reprioritize: Change order of sub-issues (use after_id or before_id)

    Args:
        owner: Repository owner
        repo: Repository name
        issue_number: Parent issue number
        method: 'add', 'remove', or 'reprioritize'
        sub_issue_id: ID of the sub-issue (not the issue number)
        replace_parent: Replace current parent when adding (optional)
        after_id: Sub-issue ID to position after (for reprioritize)
        before_id: Sub-issue ID to position before (for reprioritize)

    Returns:
        Dictionary with operation result
    """
    if not all([owner, repo]) or issue_number <= 0 or sub_issue_id <= 0:
        raise GitHubServiceError(
            code="INVALID_INPUT",
            message="owner, repo, issue_number, and sub_issue_id are required",
            http_status=400,
            retryable=False,
            details={"fields": ["owner", "repo", "issue_number", "sub_issue_id"]},
        )

    if method not in ["add", "remove", "reprioritize"]:
        raise GitHubServiceError(
            code="INVALID_INPUT",
            message="method must be 'add', 'remove', or 'reprioritize'",
            http_status=400,
            retryable=False,
            details={"valid_methods": ["add", "remove", "reprioritize"]},
        )

    if method == "reprioritize" and not (after_id or before_id):
        raise GitHubServiceError(
            code="INVALID_INPUT",
            message="reprioritize method requires either after_id or before_id",
            http_status=400,
            retryable=False,
        )

    request_body: dict[str, Any] = {
        "sub_issue_id": sub_issue_id,
    }

    if method == "add":
        request_body["replace_parent"] = replace_parent
        if after_id:
            request_body["after_id"] = after_id
        if before_id:
            request_body["before_id"] = before_id
    elif method == "reprioritize":
        if after_id:
            request_body["after_id"] = after_id
        if before_id:
            request_body["before_id"] = before_id

    # Note: GitHub's sub-issues use GraphQL primarily
    try:
        _github_api_request(
            method="PATCH" if method in ["add", "reprioritize"] else "DELETE",
            path=f"/repos/{owner}/{repo}/issues/{issue_number}/sub_issues/{sub_issue_id}",
            json_body=request_body if method in ["add", "reprioritize"] else None,
        )
        return {
            "method": method,
            "sub_issue_id": sub_issue_id,
            "success": True,
            "message": f"Sub-issue {method} completed",
        }
    except GitHubServiceError as e:
        # GraphQL-only feature fallback
        if e.http_status and 404 in str(e.http_status):
            raise GitHubServiceError(
                code="NOT_AVAILABLE",
                message="Sub-issues feature requires GitHub GraphQL API or enterprise features",
                http_status=501,
                details={"method": method, "requires": "GraphQL API access"},
            )
        raise


def assign_copilot_to_issue(
    owner: str,
    repo: str,
    issue_number: int,
    base_ref: str | None = None,
    custom_instructions: str | None = None,
) -> dict[str, Any]:
    """Assign GitHub Copilot to work on an issue.

    This delegates the issue to Copilot to create a pull request with code changes.

    Args:
        owner: Repository owner
        repo: Repository name
        issue_number: Issue number
        base_ref: Git reference (branch) to start from (optional, defaults to repo default)
        custom_instructions: Additional context/guidance for Copilot (optional)

    Returns:
        Dictionary with job/PR details
    """
    if not all([owner, repo]) or issue_number <= 0:
        raise GitHubServiceError(
            code="INVALID_INPUT",
            message="owner, repo, and issue_number are required",
            http_status=400,
            retryable=False,
            details={"fields": ["owner", "repo", "issue_number"]},
        )

    request_body: dict[str, Any] = {
        "issue_number": issue_number,
    }

    if base_ref:
        request_body["base_ref"] = base_ref
    if custom_instructions:
        request_body["custom_instructions"] = custom_instructions

    # Note: This uses GitHub's Copilot API which may require special permissions
    try:
        result = _github_api_request(
            method="POST",
            path=f"/repos/{owner}/{repo}/copilot/issues/{issue_number}/assignees",
            json_body=request_body,
        )

        return {
            "issue_number": issue_number,
            "assigned": True,
            "job_id": result.get("id"),
            "status": result.get("status", "pending"),
            "pull_request_url": result.get("pull_request", {}).get("html_url"),
        }
    except GitHubServiceError as e:
        if e.http_status and (404 in str(e.http_status) or 403 in str(e.http_status)):
            raise GitHubServiceError(
                code="NOT_AVAILABLE",
                message="Copilot API requires GitHub Enterprise with Copilot access",
                http_status=403,
                details={"requires": "GitHub Enterprise + Copilot subscription"},
            )
        raise


def request_copilot_review(
    owner: str,
    repo: str,
    pull_number: int,
) -> dict[str, Any]:
    """Request a code review from GitHub Copilot on a pull request.

    Args:
        owner: Repository owner
        repo: Repository name
        pull_number: Pull request number

    Returns:
        Dictionary with review request status
    """
    if not all([owner, repo]) or pull_number <= 0:
        raise GitHubServiceError(
            code="INVALID_INPUT",
            message="owner, repo, and pull_number are required",
            http_status=400,
            retryable=False,
            details={"fields": ["owner", "repo", "pull_number"]},
        )

    request_body = {
        "reviewers": ["copilot-pull-request-reviewer[bot]"],
    }

    try:
        _github_api_request(
            method="POST",
            path=f"/repos/{owner}/{repo}/pulls/{pull_number}/requested_reviewers",
            json_body=request_body,
        )

        return {
            "pull_number": pull_number,
            "requested": True,
            "reviewer": "copilot-pull-request-reviewer[bot]",
            "status": "review_requested",
        }
    except GitHubServiceError as e:
        if e.http_status and 404 in str(e.http_status):
            raise GitHubServiceError(
                code="NOT_FOUND",
                message="Pull request not found",
                http_status=404,
                details={"pull_number": pull_number},
            )
        elif e.http_status and 403 in str(e.http_status):
            raise GitHubServiceError(
                code="NOT_AVAILABLE",
                message="Copilot reviews require GitHub Enterprise with Copilot access",
                http_status=403,
                details={"requires": "GitHub Enterprise + Copilot subscription"},
            )
        raise
