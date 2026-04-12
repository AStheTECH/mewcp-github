import json
import logging

from fastmcp import FastMCP
from pydantic import Field

from .config import TOOL_REQUIRED_SCOPES
from .response import error_response, success_response
from .schemas import GitHubTokenData
from .service import (
    GitHubServiceError,
    add_issue_comment,
    create_branch,
    create_issue,
    create_or_update_file,
    create_repository,
    fork_repository,
    get_file_contents,
    get_commit,
    get_issue,
    get_issue_comments,
    get_repo as get_repo_service,
    get_tag,
    list_branches,
    list_commits,
    list_issues,
    list_org_repositories_by_contributor,
    list_tags,
    push_files,
    search_repositories,
    search_code,
    search_users,
    search_issues,
    update_issue,
)

logger = logging.getLogger("github-mcp-server")


def register_tools(mcp: FastMCP) -> None:
    @mcp.tool(
        name="ping",
        description="Basic health check for CL GitHub MCP server.",
    )
    def ping() -> str:
        return json.dumps(
            success_response("ping", {"status": "ok", "server": "CL GitHub MCP Server"})
        )

    @mcp.tool(
        name="get_repo",
        description="Get basic details for a GitHub repository.",
    )
    def get_repo(
        oauth_token: GitHubTokenData = Field(
            ..., description="GitHub token with token and optional scopes"
        ),
        owner: str = Field(..., description="Repository owner, for example octocat"),
        repo: str = Field(..., description="Repository name"),
    ) -> str:
        try:
            result = get_repo_service(oauth_token, owner, repo)
            granted_scopes = oauth_token.scopes
            return json.dumps(
                success_response(
                    "get_repo",
                    result,
                    meta={
                        "scope_check": {
                            "required": TOOL_REQUIRED_SCOPES["get_repo"],
                            "granted": granted_scopes,
                            "passed": True,
                        }
                    },
                )
            )
        except GitHubServiceError as exc:
            logger.error("Failed get_repo for %s/%s: %s", owner, repo, exc.message)
            return json.dumps(
                error_response(
                    "get_repo",
                    code=exc.code,
                    message=exc.message,
                    http_status=exc.http_status,
                    retryable=exc.retryable,
                    details=exc.details,
                )
            )
        except Exception as exc:
            logger.error("Failed get_repo for %s/%s: %s", owner, repo, exc)
            return json.dumps(
                error_response(
                    "get_repo",
                    code="INTERNAL_ERROR",
                    message="Unexpected error while processing get_repo.",
                    details={"exception": str(exc)},
                )
            )

    @mcp.tool(
        name="list_branches",
        description="List branches in a GitHub repository.",
    )
    def list_branches_tool(
        oauth_token: GitHubTokenData = Field(
            ..., description="GitHub token input with token and optional scopes"
        ),
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        page: int = Field(1, description="Page number"),
        perPage: int = Field(30, description="Items per page"),
    ) -> str:
        try:
            data = list_branches(oauth_token, owner, repo, page=page, per_page=perPage)
            granted_scopes = oauth_token.scopes
            return json.dumps(
                success_response(
                    "list_branches",
                    data,
                    meta={
                        "scope_check": {
                            "required": TOOL_REQUIRED_SCOPES["list_branches"],
                            "granted": granted_scopes,
                            "passed": True,
                        },
                        "pagination": {
                            "page": page,
                            "perPage": perPage,
                        },
                    },
                )
            )
        except GitHubServiceError as exc:
            logger.error("Failed list_branches for %s/%s: %s", owner, repo, exc.message)
            return json.dumps(
                error_response(
                    "list_branches",
                    code=exc.code,
                    message=exc.message,
                    http_status=exc.http_status,
                    retryable=exc.retryable,
                    details=exc.details,
                )
            )
        except Exception as exc:
            logger.error("Failed list_branches for %s/%s: %s", owner, repo, exc)
            return json.dumps(
                error_response(
                    "list_branches",
                    code="INTERNAL_ERROR",
                    message="Unexpected error while processing list_branches.",
                    details={"exception": str(exc)},
                )
            )

    @mcp.tool(
        name="search_repositories",
        description="Search GitHub repositories.",
    )
    def search_repositories_tool(
        oauth_token: GitHubTokenData = Field(
            ..., description="GitHub token input with token and optional scopes"
        ),
        query: str = Field(..., description="Search query"),
        sort: str = Field("stars", description="Sort by: stars, forks, updated"),
        order: str = Field("desc", description="Order: asc or desc"),
        page: int = Field(1, description="Page number"),
        perPage: int = Field(30, description="Items per page"),
    ) -> str:
        try:
            data = search_repositories(
                oauth_token, query, sort=sort, order=order, page=page, per_page=perPage
            )
            granted_scopes = oauth_token.scopes
            return json.dumps(
                success_response(
                    "search_repositories",
                    data,
                    meta={
                        "scope_check": {
                            "required": TOOL_REQUIRED_SCOPES["search_repositories"],
                            "granted": granted_scopes,
                            "passed": True,
                        }
                    },
                )
            )
        except GitHubServiceError as exc:
            logger.error("Failed search_repositories: %s", exc.message)
            return json.dumps(
                error_response(
                    "search_repositories",
                    code=exc.code,
                    message=exc.message,
                    http_status=exc.http_status,
                    retryable=exc.retryable,
                    details=exc.details,
                )
            )
        except Exception as exc:
            logger.error("Failed search_repositories: %s", exc)
            return json.dumps(
                error_response(
                    "search_repositories",
                    code="INTERNAL_ERROR",
                    message="Unexpected error while searching repositories.",
                    details={"exception": str(exc)},
                )
            )

    @mcp.tool(
        name="list_commits",
        description="List commits in a GitHub repository.",
    )
    def list_commits_tool(
        oauth_token: GitHubTokenData = Field(
            ..., description="GitHub token input with token and optional scopes"
        ),
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        sha: str | None = Field(None, description="Branch or commit SHA"),
        path: str | None = Field(None, description="Filter commits by path"),
        author: str | None = Field(None, description="Filter by author login"),
        since: str | None = Field(None, description="ISO 8601 date: YYYY-MM-DD"),
        until: str | None = Field(None, description="ISO 8601 date: YYYY-MM-DD"),
        page: int = Field(1, description="Page number"),
        perPage: int = Field(30, description="Items per page"),
    ) -> str:
        try:
            data = list_commits(
                oauth_token,
                owner,
                repo,
                sha=sha,
                path=path,
                author=author,
                since=since,
                until=until,
                page=page,
                per_page=perPage,
            )
            granted_scopes = oauth_token.scopes
            return json.dumps(
                success_response(
                    "list_commits",
                    data,
                    meta={
                        "scope_check": {
                            "required": TOOL_REQUIRED_SCOPES["list_commits"],
                            "granted": granted_scopes,
                            "passed": True,
                        }
                    },
                )
            )
        except GitHubServiceError as exc:
            logger.error("Failed list_commits for %s/%s: %s", owner, repo, exc.message)
            return json.dumps(
                error_response(
                    "list_commits",
                    code=exc.code,
                    message=exc.message,
                    http_status=exc.http_status,
                    retryable=exc.retryable,
                    details=exc.details,
                )
            )
        except Exception as exc:
            logger.error("Failed list_commits for %s/%s: %s", owner, repo, exc)
            return json.dumps(
                error_response(
                    "list_commits",
                    code="INTERNAL_ERROR",
                    message="Unexpected error while listing commits.",
                    details={"exception": str(exc)},
                )
            )

    @mcp.tool(
        name="get_commit",
        description="Get details of a specific commit.",
    )
    def get_commit_tool(
        oauth_token: GitHubTokenData = Field(
            ..., description="GitHub token input with token and optional scopes"
        ),
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        sha: str = Field(..., description="Commit SHA"),
        include_diff: bool = Field(True, description="Include file changes in diff"),
    ) -> str:
        try:
            data = get_commit(oauth_token, owner, repo, sha, include_diff=include_diff)
            granted_scopes = oauth_token.scopes
            return json.dumps(
                success_response(
                    "get_commit",
                    data,
                    meta={
                        "scope_check": {
                            "required": TOOL_REQUIRED_SCOPES["get_commit"],
                            "granted": granted_scopes,
                            "passed": True,
                        }
                    },
                )
            )
        except GitHubServiceError as exc:
            logger.error(
                "Failed get_commit for %s/%s:%s: %s", owner, repo, sha, exc.message
            )
            return json.dumps(
                error_response(
                    "get_commit",
                    code=exc.code,
                    message=exc.message,
                    http_status=exc.http_status,
                    retryable=exc.retryable,
                    details=exc.details,
                )
            )
        except Exception as exc:
            logger.error("Failed get_commit for %s/%s:%s: %s", owner, repo, sha, exc)
            return json.dumps(
                error_response(
                    "get_commit",
                    code="INTERNAL_ERROR",
                    message="Unexpected error while fetching commit.",
                    details={"exception": str(exc)},
                )
            )

    @mcp.tool(
        name="list_issues",
        description="List issues in a GitHub repository.",
    )
    def list_issues_tool(
        oauth_token: GitHubTokenData = Field(
            ..., description="GitHub token input with token and optional scopes"
        ),
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        state: str = Field("open", description="Filter by state: open, closed, all"),
        labels: str | None = Field(
            None, description="Comma-separated label names to filter by"
        ),
        page: int = Field(1, description="Page number"),
        perPage: int = Field(30, description="Items per page"),
    ) -> str:
        try:
            data = list_issues(
                oauth_token,
                owner,
                repo,
                state=state,
                labels=labels,
                page=page,
                per_page=perPage,
            )
            granted_scopes = oauth_token.scopes
            return json.dumps(
                success_response(
                    "list_issues",
                    data,
                    meta={
                        "scope_check": {
                            "required": TOOL_REQUIRED_SCOPES["list_issues"],
                            "granted": granted_scopes,
                            "passed": True,
                        }
                    },
                )
            )
        except GitHubServiceError as exc:
            logger.error("Failed list_issues for %s/%s: %s", owner, repo, exc.message)
            return json.dumps(
                error_response(
                    "list_issues",
                    code=exc.code,
                    message=exc.message,
                    http_status=exc.http_status,
                    retryable=exc.retryable,
                    details=exc.details,
                )
            )
        except Exception as exc:
            logger.error("Failed list_issues for %s/%s: %s", owner, repo, exc)
            return json.dumps(
                error_response(
                    "list_issues",
                    code="INTERNAL_ERROR",
                    message="Unexpected error while listing issues.",
                    details={"exception": str(exc)},
                )
            )

    @mcp.tool(
        name="get_file_contents",
        description="Get file or directory contents from a GitHub repository.",
    )
    def get_file_contents_tool(
        oauth_token: GitHubTokenData = Field(
            ..., description="GitHub token input with token and optional scopes"
        ),
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        path: str = Field("/", description="File or directory path"),
        ref: str | None = Field(None, description="Branch, tag, or commit SHA"),
    ) -> str:
        try:
            data = get_file_contents(oauth_token, owner, repo, path=path, ref=ref)
            granted_scopes = oauth_token.scopes
            return json.dumps(
                success_response(
                    "get_file_contents",
                    data,
                    meta={
                        "scope_check": {
                            "required": TOOL_REQUIRED_SCOPES["get_file_contents"],
                            "granted": granted_scopes,
                            "passed": True,
                        }
                    },
                )
            )
        except GitHubServiceError as exc:
            logger.error(
                "Failed get_file_contents for %s/%s:%s: %s",
                owner,
                repo,
                path,
                exc.message,
            )
            return json.dumps(
                error_response(
                    "get_file_contents",
                    code=exc.code,
                    message=exc.message,
                    http_status=exc.http_status,
                    retryable=exc.retryable,
                    details=exc.details,
                )
            )
        except Exception as exc:
            logger.error(
                "Failed get_file_contents for %s/%s:%s: %s", owner, repo, path, exc
            )
            return json.dumps(
                error_response(
                    "get_file_contents",
                    code="INTERNAL_ERROR",
                    message="Unexpected error while fetching file contents.",
                    details={"exception": str(exc)},
                )
            )

    @mcp.tool(
        name="search_code",
        description="Fast and precise code search across GitHub repositories using GitHub's native search engine. Best for finding exact symbols, functions, classes, or specific code patterns.",
    )
    def search_code_tool(
        oauth_token: GitHubTokenData = Field(
            ...,
            description="GitHub personal access token or OAuth token (with repo scope)",
        ),
        query: str = Field(
            ...,
            description="Search query using GitHub code search syntax. Examples: 'content:Skill language:Java org:github', 'NOT is:archived language:Python OR language:go', 'repo:github/github-mcp-server', 'filename:test.py', 'path:src/components'. Supports exact matching, language filters, path filters, org filters, and more.",
        ),
        sort: str = Field(
            "indexed",
            description="Sort field for results. Only 'indexed' is supported (by relevance). Default: 'indexed'.",
        ),
        order: str = Field(
            "desc",
            description="Sort order for results. Options: 'asc' (ascending) or 'desc' (descending). Default: 'desc'.",
        ),
        page: int = Field(
            1,
            description="Page number for pagination. Starts at 1. Use with perPage to browse results. Default: 1.",
        ),
        perPage: int = Field(
            30,
            description="Number of results per page. Range: 1-100. Default: 30. Increase for fewer API calls, decrease for smaller responses.",
        ),
    ) -> str:
        try:
            data = search_code(
                oauth_token, query, sort=sort, order=order, page=page, per_page=perPage
            )
            granted_scopes = oauth_token.scopes
            return json.dumps(
                success_response(
                    "search_code",
                    data,
                    meta={
                        "scope_check": {
                            "required": TOOL_REQUIRED_SCOPES["search_code"],
                            "granted": granted_scopes,
                            "passed": True,
                        },
                        "pagination": {
                            "page": page,
                            "perPage": perPage,
                        },
                    },
                )
            )
        except GitHubServiceError as exc:
            logger.error("Failed search_code: %s", exc.message)
            return json.dumps(
                error_response(
                    "search_code",
                    code=exc.code,
                    message=exc.message,
                    http_status=exc.http_status,
                    retryable=exc.retryable,
                    details=exc.details,
                )
            )
        except Exception as exc:
            logger.error("Failed search_code: %s", exc)
            return json.dumps(
                error_response(
                    "search_code",
                    code="INTERNAL_ERROR",
                    message="Unexpected error while searching code.",
                    details={"exception": str(exc)},
                )
            )

    @mcp.tool(
        name="search_users",
        description="Search GitHub users by name, location, followers, or other attributes. Returns user profiles with login, ID, and avatar URL for further investigation.",
    )
    def search_users_tool(
        oauth_token: GitHubTokenData = Field(
            ...,
            description="GitHub personal access token or OAuth token (with repo scope)",
        ),
        query: str = Field(
            ...,
            description="User search query using GitHub's search syntax. Examples: 'john smith', 'location:seattle', 'followers:>100', 'repos:>50 language:python'. Support full name, location, follower counts, repository counts, and more.",
        ),
        sort: str = Field(
            "followers",
            description="Sort field for user results. Options: 'followers' (most followers first), 'repositories' (most repos first), 'joined' (newest users first). Default: 'followers'.",
        ),
        order: str = Field(
            "desc",
            description="Sort order for results. Options: 'asc' (ascending) or 'desc' (descending). Default: 'desc' (most relevant first).",
        ),
        page: int = Field(
            1,
            description="Page number for pagination. Starts at 1. Use with perPage to browse results. Default: 1.",
        ),
        perPage: int = Field(
            30,
            description="Number of results per page. Range: 1-100. Default: 30. Increase for fewer API calls, decrease for smaller responses.",
        ),
    ) -> str:
        try:
            data = search_users(
                oauth_token, query, sort=sort, order=order, page=page, per_page=perPage
            )
            granted_scopes = oauth_token.scopes
            return json.dumps(
                success_response(
                    "search_users",
                    data,
                    meta={
                        "scope_check": {
                            "required": TOOL_REQUIRED_SCOPES["search_users"],
                            "granted": granted_scopes,
                            "passed": True,
                        },
                        "pagination": {
                            "page": page,
                            "perPage": perPage,
                        },
                    },
                )
            )
        except GitHubServiceError as exc:
            logger.error("Failed search_users: %s", exc.message)
            return json.dumps(
                error_response(
                    "search_users",
                    code=exc.code,
                    message=exc.message,
                    http_status=exc.http_status,
                    retryable=exc.retryable,
                    details=exc.details,
                )
            )
        except Exception as exc:
            logger.error("Failed search_users: %s", exc)
            return json.dumps(
                error_response(
                    "search_users",
                    code="INTERNAL_ERROR",
                    message="Unexpected error while searching users.",
                    details={"exception": str(exc)},
                )
            )

    @mcp.tool(
        name="search_issues",
        description="Search issues and pull requests across GitHub. Filter by state, labels, creator, assignee, and more. Use owner+repo parameters to scope search to specific repositories.",
    )
    def search_issues_tool(
        oauth_token: GitHubTokenData = Field(
            ...,
            description="GitHub personal access token or OAuth token (with repo scope)",
        ),
        query: str = Field(
            ...,
            description="Search query using GitHub issue search syntax. Examples: 'is:open label:bug', 'is:closed author:octocat', 'type:issue state:open label:enhancement'. Supports state filters, label filters, author filters, assignee filters, and more.",
        ),
        sort: str = Field(
            "updated",
            description="Sort field for issue results. Options: 'updated', 'created', 'comments'. Default: 'updated' (most recently updated first).",
        ),
        order: str = Field(
            "desc",
            description="Sort order for results. Options: 'asc' (ascending) or 'desc' (descending). Default: 'desc' (most recent first).",
        ),
        owner: str | None = Field(
            None,
            description="Repository owner name. Optional, but when provided must be paired with 'repo' parameter to scope search to specific repository. Example: 'github'.",
        ),
        repo: str | None = Field(
            None,
            description="Repository name. Optional, but when provided must be paired with 'owner' parameter to scope search to specific repository. Example: 'github-mcp-server'.",
        ),
        page: int = Field(
            1,
            description="Page number for pagination. Starts at 1. Use with perPage to browse results. Default: 1.",
        ),
        perPage: int = Field(
            30,
            description="Number of results per page. Range: 1-100. Default: 30. Increase for fewer API calls, decrease for smaller responses.",
        ),
    ) -> str:
        try:
            data = search_issues(
                oauth_token,
                query,
                sort=sort,
                order=order,
                owner=owner,
                repo=repo,
                page=page,
                per_page=perPage,
            )
            granted_scopes = oauth_token.scopes
            return json.dumps(
                success_response(
                    "search_issues",
                    data,
                    meta={
                        "scope_check": {
                            "required": TOOL_REQUIRED_SCOPES["search_issues"],
                            "granted": granted_scopes,
                            "passed": True,
                        },
                        "pagination": {
                            "page": page,
                            "perPage": perPage,
                        },
                    },
                )
            )
        except GitHubServiceError as exc:
            logger.error("Failed search_issues: %s", exc.message)
            return json.dumps(
                error_response(
                    "search_issues",
                    code=exc.code,
                    message=exc.message,
                    http_status=exc.http_status,
                    retryable=exc.retryable,
                    details=exc.details,
                )
            )
        except Exception as exc:
            logger.error("Failed search_issues: %s", exc)
            return json.dumps(
                error_response(
                    "search_issues",
                    code="INTERNAL_ERROR",
                    message="Unexpected error while searching issues.",
                    details={"exception": str(exc)},
                )
            )

    @mcp.tool(
        name="get_issue",
        description="Get detailed information about a specific GitHub issue including title, body, state, labels, assignees, and timestamps.",
    )
    def get_issue_tool(
        oauth_token: GitHubTokenData = Field(
            ...,
            description="GitHub personal access token or OAuth token (with repo or public_repo scope)",
        ),
        owner: str = Field(
            ..., description="Repository owner name. Example: 'github'."
        ),
        repo: str = Field(
            ..., description="Repository name. Example: 'github-mcp-server'."
        ),
        issue_number: int = Field(
            ...,
            description="Issue number (unique identifier for the issue in this repository). Example: 123.",
        ),
    ) -> str:
        try:
            data = get_issue(oauth_token, owner, repo, issue_number)
            granted_scopes = oauth_token.scopes
            return json.dumps(
                success_response(
                    "get_issue",
                    data,
                    meta={
                        "scope_check": {
                            "required": TOOL_REQUIRED_SCOPES["get_issue"],
                            "granted": granted_scopes,
                            "passed": True,
                        }
                    },
                )
            )
        except GitHubServiceError as exc:
            logger.error(
                "Failed get_issue for %s/%s#%d: %s",
                owner,
                repo,
                issue_number,
                exc.message,
            )
            return json.dumps(
                error_response(
                    "get_issue",
                    code=exc.code,
                    message=exc.message,
                    http_status=exc.http_status,
                    retryable=exc.retryable,
                    details=exc.details,
                )
            )
        except Exception as exc:
            logger.error(
                "Failed get_issue for %s/%s#%d: %s", owner, repo, issue_number, exc
            )
            return json.dumps(
                error_response(
                    "get_issue",
                    code="INTERNAL_ERROR",
                    message="Unexpected error while fetching issue details.",
                    details={"exception": str(exc)},
                )
            )

    @mcp.tool(
        name="get_issue_comments",
        description="Get all comments on a GitHub issue with pagination support. Returns comment body, author, creation time, and timestamps.",
    )
    def get_issue_comments_tool(
        oauth_token: GitHubTokenData = Field(
            ...,
            description="GitHub personal access token or OAuth token (with repo or public_repo scope)",
        ),
        owner: str = Field(
            ..., description="Repository owner name. Example: 'github'."
        ),
        repo: str = Field(
            ..., description="Repository name. Example: 'github-mcp-server'."
        ),
        issue_number: int = Field(
            ...,
            description="Issue number (unique identifier for the issue in this repository). Example: 123.",
        ),
        page: int = Field(
            1,
            description="Page number for pagination. Starts at 1. Use with perPage to browse through comment threads. Default: 1.",
        ),
        perPage: int = Field(
            30,
            description="Number of comments per page. Range: 1-100. Default: 30. Increase to fetch more comments per request, decrease for smaller payloads.",
        ),
    ) -> str:
        try:
            data = get_issue_comments(
                oauth_token, owner, repo, issue_number, page=page, per_page=perPage
            )
            granted_scopes = oauth_token.scopes
            return json.dumps(
                success_response(
                    "get_issue_comments",
                    data,
                    meta={
                        "scope_check": {
                            "required": TOOL_REQUIRED_SCOPES["get_issue_comments"],
                            "granted": granted_scopes,
                            "passed": True,
                        },
                        "pagination": {
                            "page": page,
                            "perPage": perPage,
                        },
                    },
                )
            )
        except GitHubServiceError as exc:
            logger.error(
                "Failed get_issue_comments for %s/%s#%d: %s",
                owner,
                repo,
                issue_number,
                exc.message,
            )
            return json.dumps(
                error_response(
                    "get_issue_comments",
                    code=exc.code,
                    message=exc.message,
                    http_status=exc.http_status,
                    retryable=exc.retryable,
                    details=exc.details,
                )
            )
        except Exception as exc:
            logger.error(
                "Failed get_issue_comments for %s/%s#%d: %s",
                owner,
                repo,
                issue_number,
                exc,
            )
            return json.dumps(
                error_response(
                    "get_issue_comments",
                    code="INTERNAL_ERROR",
                    message="Unexpected error while fetching issue comments.",
                    details={"exception": str(exc)},
                )
            )

    @mcp.tool(
        name="create_issue",
        description="Create a new GitHub issue in a repository. Returns the issue ID, number, and URL on successful creation.",
    )
    def create_issue_tool(
        oauth_token: GitHubTokenData = Field(
            ...,
            description="GitHub personal access token or OAuth token (with repo scope)",
        ),
        owner: str = Field(
            ..., description="Repository owner name. Example: 'github'."
        ),
        repo: str = Field(
            ..., description="Repository name. Example: 'github-mcp-server'."
        ),
        title: str = Field(
            ...,
            description="Issue title (required). Visible on the issue page. Example: 'Fix authentication bug'.",
        ),
        body: str | None = Field(
            None,
            description="Issue description (optional). Supports GitHub markdown formatting. Can include code blocks, lists, links, etc.",
        ),
        assignees: list[str] | None = Field(
            None,
            description="List of GitHub usernames to assign to this issue (optional). Example: ['user1', 'user2']. Users must have repository access.",
        ),
        labels: list[str] | None = Field(
            None,
            description="List of label names to add to this issue (optional). Example: ['bug', 'urgent']. Labels must exist in the repository.",
        ),
        milestone: int | None = Field(
            None,
            description="Milestone ID to associate with this issue (optional). Must be a valid milestone in the repository.",
        ),
    ) -> str:
        try:
            data = create_issue(
                oauth_token,
                owner,
                repo,
                title,
                body=body,
                assignees=assignees,
                labels=labels,
                milestone=milestone,
            )
            granted_scopes = oauth_token.scopes
            return json.dumps(
                success_response(
                    "create_issue",
                    data,
                    meta={
                        "scope_check": {
                            "required": TOOL_REQUIRED_SCOPES["create_issue"],
                            "granted": granted_scopes,
                            "passed": True,
                        }
                    },
                )
            )
        except GitHubServiceError as exc:
            logger.error("Failed create_issue for %s/%s: %s", owner, repo, exc.message)
            return json.dumps(
                error_response(
                    "create_issue",
                    code=exc.code,
                    message=exc.message,
                    http_status=exc.http_status,
                    retryable=exc.retryable,
                    details=exc.details,
                )
            )
        except Exception as exc:
            logger.error("Failed create_issue for %s/%s: %s", owner, repo, exc)
            return json.dumps(
                error_response(
                    "create_issue",
                    code="INTERNAL_ERROR",
                    message="Unexpected error while creating issue.",
                    details={"exception": str(exc)},
                )
            )

    @mcp.tool(
        name="add_issue_comment",
        description="Add a comment to a GitHub issue or pull request. Comments support GitHub markdown formatting.",
    )
    def add_issue_comment_tool(
        oauth_token: GitHubTokenData = Field(
            ...,
            description="GitHub personal access token or OAuth token (with repo scope)",
        ),
        owner: str = Field(
            ..., description="Repository owner name. Example: 'github'."
        ),
        repo: str = Field(
            ..., description="Repository name. Example: 'github-mcp-server'."
        ),
        issue_number: int = Field(
            ..., description="Issue or pull request number. Example: 123."
        ),
        body: str = Field(
            ...,
            description="Comment text (required). Supports GitHub markdown formatting including code blocks, mentions (@username), and reactions.",
        ),
    ) -> str:
        try:
            data = add_issue_comment(oauth_token, owner, repo, issue_number, body)
            granted_scopes = oauth_token.scopes
            return json.dumps(
                success_response(
                    "add_issue_comment",
                    data,
                    meta={
                        "scope_check": {
                            "required": TOOL_REQUIRED_SCOPES["add_issue_comment"],
                            "granted": granted_scopes,
                            "passed": True,
                        }
                    },
                )
            )
        except GitHubServiceError as exc:
            logger.error(
                "Failed add_issue_comment for %s/%s#%d: %s",
                owner,
                repo,
                issue_number,
                exc.message,
            )
            return json.dumps(
                error_response(
                    "add_issue_comment",
                    code=exc.code,
                    message=exc.message,
                    http_status=exc.http_status,
                    retryable=exc.retryable,
                    details=exc.details,
                )
            )
        except Exception as exc:
            logger.error(
                "Failed add_issue_comment for %s/%s#%d: %s",
                owner,
                repo,
                issue_number,
                exc,
            )
            return json.dumps(
                error_response(
                    "add_issue_comment",
                    code="INTERNAL_ERROR",
                    message="Unexpected error while adding comment.",
                    details={"exception": str(exc)},
                )
            )

    @mcp.tool(
        name="update_issue",
        description="Update GitHub issue properties including title, body, state (open/closed), assignees, and labels. Provide only fields you want to change.",
    )
    def update_issue_tool(
        oauth_token: GitHubTokenData = Field(
            ...,
            description="GitHub personal access token or OAuth token (with repo scope)",
        ),
        owner: str = Field(
            ..., description="Repository owner name. Example: 'github'."
        ),
        repo: str = Field(
            ..., description="Repository name. Example: 'github-mcp-server'."
        ),
        issue_number: int = Field(
            ..., description="Issue number to update. Example: 123."
        ),
        title: str | None = Field(
            None,
            description="New issue title (optional). Leave empty to keep current title.",
        ),
        body: str | None = Field(
            None,
            description="New issue description (optional). Supports GitHub markdown. Leave empty to keep current body.",
        ),
        state: str | None = Field(
            None,
            description="New state for the issue (optional). Options: 'open' or 'closed'. Leave empty to keep current state.",
        ),
        state_reason: str | None = Field(
            None,
            description="Reason for state change when closing (optional). Options: 'completed', 'not_planned'. Only used when state='closed'.",
        ),
        assignees: list[str] | None = Field(
            None,
            description="New list of assignees (optional). Replaces current assignees. Pass empty list to clear assignments.",
        ),
        labels: list[str] | None = Field(
            None,
            description="New list of labels (optional). Replaces current labels. Pass empty list to clear labels.",
        ),
        milestone: int | None = Field(
            None,
            description="Milestone ID (optional). Pass 0 or null to remove milestone.",
        ),
    ) -> str:
        try:
            data = update_issue(
                oauth_token,
                owner,
                repo,
                issue_number,
                title=title,
                body=body,
                state=state,
                state_reason=state_reason,
                assignees=assignees,
                labels=labels,
                milestone=milestone,
            )
            granted_scopes = oauth_token.scopes
            return json.dumps(
                success_response(
                    "update_issue",
                    data,
                    meta={
                        "scope_check": {
                            "required": TOOL_REQUIRED_SCOPES["update_issue"],
                            "granted": granted_scopes,
                            "passed": True,
                        }
                    },
                )
            )
        except GitHubServiceError as exc:
            logger.error(
                "Failed update_issue for %s/%s#%d: %s",
                owner,
                repo,
                issue_number,
                exc.message,
            )
            return json.dumps(
                error_response(
                    "update_issue",
                    code=exc.code,
                    message=exc.message,
                    http_status=exc.http_status,
                    retryable=exc.retryable,
                    details=exc.details,
                )
            )
        except Exception as exc:
            logger.error(
                "Failed update_issue for %s/%s#%d: %s",
                owner,
                repo,
                issue_number,
                exc,
            )
            return json.dumps(
                error_response(
                    "update_issue",
                    code="INTERNAL_ERROR",
                    message="Unexpected error while updating issue.",
                    details={"exception": str(exc)},
                )
            )

    @mcp.tool(
        name="list_org_repositories_by_contributor",
        description="Find all repositories in an organization where specific contributors have made contributions.",
    )
    def list_org_repositories_by_contributor_tool(
        oauth_token: GitHubTokenData = Field(
            ..., description="GitHub token input with token and optional scopes"
        ),
        org: str = Field(..., description="Organization name"),
        contributor_usernames: str = Field(
            ...,
            description="GitHub username(s) to filter repositories by. Use comma-separated values for multiple users (e.g., 'user1,user2,user3')",
        ),
        repo_type: str = Field(
            "all",
            description="Filter by repository type: all, public, or private (default: all)",
        ),
    ) -> str:
        try:
            # Parse comma-separated usernames or single username
            usernames_list = [
                u.strip() for u in contributor_usernames.split(",") if u.strip()
            ]

            data = list_org_repositories_by_contributor(
                oauth_token, org, usernames_list, repo_type=repo_type
            )
            granted_scopes = oauth_token.scopes
            return json.dumps(
                success_response(
                    "list_org_repositories_by_contributor",
                    data,
                    meta={
                        "scope_check": {
                            "required": TOOL_REQUIRED_SCOPES[
                                "list_org_repositories_by_contributor"
                            ],
                            "granted": granted_scopes,
                            "passed": True,
                        }
                    },
                )
            )
        except GitHubServiceError as exc:
            logger.error(
                "Failed list_org_repositories_by_contributor for %s/%s: %s",
                org,
                contributor_usernames,
                exc.message,
            )
            return json.dumps(
                error_response(
                    "list_org_repositories_by_contributor",
                    code=exc.code,
                    message=exc.message,
                    http_status=exc.http_status,
                    retryable=exc.retryable,
                    details=exc.details,
                )
            )
        except Exception as exc:
            logger.error(
                "Failed list_org_repositories_by_contributor for %s/%s: %s",
                org,
                contributor_usernames,
                exc,
            )
            return json.dumps(
                error_response(
                    "list_org_repositories_by_contributor",
                    code="INTERNAL_ERROR",
                    message="Unexpected error while finding repositories by contributor.",
                    details={"exception": str(exc)},
                )
            )

    @mcp.tool(
        name="list_tags",
        description="List all git tags in a repository with pagination support. Returns tag names, commit info, and download URLs.",
    )
    def list_tags_tool(
        oauth_token: GitHubTokenData = Field(
            ...,
            description="GitHub personal access token or OAuth token (with repo scope)",
        ),
        owner: str = Field(
            ..., description="Repository owner name. Example: 'github'."
        ),
        repo: str = Field(
            ..., description="Repository name. Example: 'github-mcp-server'."
        ),
        page: int = Field(
            1,
            description="Page number for pagination. Starts at 1. Default: 1.",
        ),
        perPage: int = Field(
            30,
            description="Number of tags per page. Range: 1-100. Default: 30.",
        ),
    ) -> str:
        try:
            data = list_tags(oauth_token, owner, repo, page=page, per_page=perPage)
            granted_scopes = oauth_token.scopes
            return json.dumps(
                success_response(
                    "list_tags",
                    data,
                    meta={
                        "scope_check": {
                            "required": TOOL_REQUIRED_SCOPES["list_tags"],
                            "granted": granted_scopes,
                            "passed": True,
                        },
                        "pagination": {
                            "page": page,
                            "perPage": perPage,
                        },
                    },
                )
            )
        except GitHubServiceError as exc:
            logger.error("Failed list_tags for %s/%s: %s", owner, repo, exc.message)
            return json.dumps(
                error_response(
                    "list_tags",
                    code=exc.code,
                    message=exc.message,
                    http_status=exc.http_status,
                    retryable=exc.retryable,
                    details=exc.details,
                )
            )
        except Exception as exc:
            logger.error("Failed list_tags for %s/%s: %s", owner, repo, exc)
            return json.dumps(
                error_response(
                    "list_tags",
                    code="INTERNAL_ERROR",
                    message="Unexpected error while listing tags.",
                    details={"exception": str(exc)},
                )
            )

    @mcp.tool(
        name="get_tag",
        description="Get detailed information about a specific git tag including commit SHA and object info.",
    )
    def get_tag_tool(
        oauth_token: GitHubTokenData = Field(
            ...,
            description="GitHub personal access token or OAuth token (with repo scope)",
        ),
        owner: str = Field(
            ..., description="Repository owner name. Example: 'github'."
        ),
        repo: str = Field(
            ..., description="Repository name. Example: 'github-mcp-server'."
        ),
        tag: str = Field(
            ...,
            description="Tag name to retrieve. Example: 'v1.0.0' or 'release-2024-01'.",
        ),
    ) -> str:
        try:
            data = get_tag(oauth_token, owner, repo, tag)
            granted_scopes = oauth_token.scopes
            return json.dumps(
                success_response(
                    "get_tag",
                    data,
                    meta={
                        "scope_check": {
                            "required": TOOL_REQUIRED_SCOPES["get_tag"],
                            "granted": granted_scopes,
                            "passed": True,
                        }
                    },
                )
            )
        except GitHubServiceError as exc:
            logger.error(
                "Failed get_tag for %s/%s:%s: %s", owner, repo, tag, exc.message
            )
            return json.dumps(
                error_response(
                    "get_tag",
                    code=exc.code,
                    message=exc.message,
                    http_status=exc.http_status,
                    retryable=exc.retryable,
                    details=exc.details,
                )
            )
        except Exception as exc:
            logger.error("Failed get_tag for %s/%s:%s: %s", owner, repo, tag, exc)
            return json.dumps(
                error_response(
                    "get_tag",
                    code="INTERNAL_ERROR",
                    message="Unexpected error while fetching tag details.",
                    details={"exception": str(exc)},
                )
            )

    @mcp.tool(
        name="create_repository",
        description="Create a new GitHub repository in your personal account or an organization.",
    )
    def create_repository_tool(
        oauth_token: GitHubTokenData = Field(
            ...,
            description="GitHub personal access token or OAuth token (with repo scope)",
        ),
        name: str = Field(
            ...,
            description="Repository name (required). Must be unique in account/organization.",
        ),
        description: str | None = Field(
            None,
            description="Repository description (optional). Shown on repository homepage.",
        ),
        private: bool = Field(
            False,
            description="Make repository private (default: False for public). Requires repo scope.",
        ),
        auto_init: bool = Field(
            False,
            description="Auto-initialize with README, .gitignore, and license (default: False).",
        ),
        gitignore_template: str | None = Field(
            None,
            description="Gitignore template name. Example: 'Python', 'Node', 'Java'. Only used with auto_init=true.",
        ),
        org: str | None = Field(
            None,
            description="Organization name to create repo in (optional). If omitted, creates in personal account.",
        ),
    ) -> str:
        try:
            data = create_repository(
                oauth_token,
                name=name,
                description=description,
                private=private,
                auto_init=auto_init,
                gitignore_template=gitignore_template,
                org=org,
            )
            granted_scopes = oauth_token.scopes
            return json.dumps(
                success_response(
                    "create_repository",
                    data,
                    meta={
                        "scope_check": {
                            "required": TOOL_REQUIRED_SCOPES["create_repository"],
                            "granted": granted_scopes,
                            "passed": True,
                        }
                    },
                )
            )
        except GitHubServiceError as exc:
            logger.error("Failed create_repository for %s: %s", name, exc.message)
            return json.dumps(
                error_response(
                    "create_repository",
                    code=exc.code,
                    message=exc.message,
                    http_status=exc.http_status,
                    retryable=exc.retryable,
                    details=exc.details,
                )
            )
        except Exception as exc:
            logger.error("Failed create_repository for %s: %s", name, exc)
            return json.dumps(
                error_response(
                    "create_repository",
                    code="INTERNAL_ERROR",
                    message="Unexpected error while creating repository.",
                    details={"exception": str(exc)},
                )
            )

    @mcp.tool(
        name="create_or_update_file",
        description="Create or update a file in a repository. Prevents accidental overwrites with SHA validation.",
    )
    def create_or_update_file_tool(
        oauth_token: GitHubTokenData = Field(
            ...,
            description="GitHub personal access token or OAuth token (with repo scope)",
        ),
        owner: str = Field(..., description="Repository owner name."),
        repo: str = Field(..., description="Repository name."),
        path: str = Field(
            ...,
            description="File path in repository. Example: 'src/main.py' or 'README.md'. Create directories as needed.",
        ),
        content: str = Field(
            ...,
            description="File content to write. For binary files, base64 encode first.",
        ),
        message: str = Field(
            ...,
            description="Commit message. Example: 'Update README with installation steps'.",
        ),
        branch: str | None = Field(
            None,
            description="Target branch name (optional). If omitted, uses repository default branch.",
        ),
        sha: str | None = Field(
            None,
            description="File SHA (optional, for updates only). Prevents overwrite conflicts. Get from get_file_contents.",
        ),
    ) -> str:
        try:
            data = create_or_update_file(
                oauth_token,
                owner=owner,
                repo=repo,
                path=path,
                content=content,
                message=message,
                branch=branch,
                sha=sha,
            )
            granted_scopes = oauth_token.scopes
            return json.dumps(
                success_response(
                    "create_or_update_file",
                    data,
                    meta={
                        "scope_check": {
                            "required": TOOL_REQUIRED_SCOPES["create_or_update_file"],
                            "granted": granted_scopes,
                            "passed": True,
                        }
                    },
                )
            )
        except GitHubServiceError as exc:
            logger.error(
                "Failed create_or_update_file for %s/%s:%s: %s",
                owner,
                repo,
                path,
                exc.message,
            )
            return json.dumps(
                error_response(
                    "create_or_update_file",
                    code=exc.code,
                    message=exc.message,
                    http_status=exc.http_status,
                    retryable=exc.retryable,
                    details=exc.details,
                )
            )
        except Exception as exc:
            logger.error(
                "Failed create_or_update_file for %s/%s:%s: %s",
                owner,
                repo,
                path,
                exc,
            )
            return json.dumps(
                error_response(
                    "create_or_update_file",
                    code="INTERNAL_ERROR",
                    message="Unexpected error while creating or updating file.",
                    details={"exception": str(exc)},
                )
            )

    @mcp.tool(
        name="fork_repository",
        description="Fork a repository to your personal account or an organization.",
    )
    def fork_repository_tool(
        oauth_token: GitHubTokenData = Field(
            ...,
            description="GitHub personal access token or OAuth token (with repo scope)",
        ),
        owner: str = Field(..., description="Original repository owner."),
        repo: str = Field(..., description="Original repository name."),
        org: str | None = Field(
            None,
            description="Organization name to fork into (optional). If omitted, forks to personal account.",
        ),
    ) -> str:
        try:
            data = fork_repository(oauth_token, owner=owner, repo=repo, org=org)
            granted_scopes = oauth_token.scopes
            return json.dumps(
                success_response(
                    "fork_repository",
                    data,
                    meta={
                        "scope_check": {
                            "required": TOOL_REQUIRED_SCOPES["fork_repository"],
                            "granted": granted_scopes,
                            "passed": True,
                        }
                    },
                )
            )
        except GitHubServiceError as exc:
            logger.error(
                "Failed fork_repository for %s/%s: %s", owner, repo, exc.message
            )
            return json.dumps(
                error_response(
                    "fork_repository",
                    code=exc.code,
                    message=exc.message,
                    http_status=exc.http_status,
                    retryable=exc.retryable,
                    details=exc.details,
                )
            )
        except Exception as exc:
            logger.error("Failed fork_repository for %s/%s: %s", owner, repo, exc)
            return json.dumps(
                error_response(
                    "fork_repository",
                    code="INTERNAL_ERROR",
                    message="Unexpected error while forking repository.",
                    details={"exception": str(exc)},
                )
            )

    @mcp.tool(
        name="create_branch",
        description="Create a new branch in a repository from source branch or commit SHA.",
    )
    def create_branch_tool(
        oauth_token: GitHubTokenData = Field(
            ...,
            description="GitHub personal access token or OAuth token (with repo scope)",
        ),
        owner: str = Field(..., description="Repository owner name."),
        repo: str = Field(..., description="Repository name."),
        branch_name: str = Field(
            ...,
            description="New branch name to create. Example: 'feature/new-feature' or 'bugfix/issue-123'.",
        ),
        sha: str | None = Field(
            None,
            description="Commit SHA to branch from (optional). If omitted, branches from default branch.",
        ),
    ) -> str:
        try:
            data = create_branch(
                oauth_token, owner=owner, repo=repo, branch_name=branch_name, sha=sha
            )
            granted_scopes = oauth_token.scopes
            return json.dumps(
                success_response(
                    "create_branch",
                    data,
                    meta={
                        "scope_check": {
                            "required": TOOL_REQUIRED_SCOPES["create_branch"],
                            "granted": granted_scopes,
                            "passed": True,
                        }
                    },
                )
            )
        except GitHubServiceError as exc:
            logger.error(
                "Failed create_branch for %s/%s:%s: %s",
                owner,
                repo,
                branch_name,
                exc.message,
            )
            return json.dumps(
                error_response(
                    "create_branch",
                    code=exc.code,
                    message=exc.message,
                    http_status=exc.http_status,
                    retryable=exc.retryable,
                    details=exc.details,
                )
            )
        except Exception as exc:
            logger.error(
                "Failed create_branch for %s/%s:%s: %s",
                owner,
                repo,
                branch_name,
                exc,
            )
            return json.dumps(
                error_response(
                    "create_branch",
                    code="INTERNAL_ERROR",
                    message="Unexpected error while creating branch.",
                    details={"exception": str(exc)},
                )
            )

    @mcp.tool(
        name="push_files",
        description="Push multiple files to a repository in a single atomic commit. Supports creating new branches and file directories.",
    )
    def push_files_tool(
        oauth_token: GitHubTokenData = Field(
            ...,
            description="GitHub personal access token or OAuth token (with repo scope)",
        ),
        owner: str = Field(..., description="Repository owner name."),
        repo: str = Field(..., description="Repository name."),
        files_json: str = Field(
            ...,
            description='JSON array of file objects with \'path\' and \'content\' keys. Example: \'[{"path": "file1.txt", "content": "hello"}, {"path": "dir/file2.txt", "content": "world"}]\'',
        ),
        message: str = Field(
            ...,
            description="Commit message describing changes.",
        ),
        branch: str | None = Field(
            None,
            description="Target branch name (optional). If omitted, uses repository default branch.",
        ),
        author_name: str | None = Field(
            None,
            description="Author name for commit (optional). If omitted, uses authenticated user.",
        ),
        author_email: str | None = Field(
            None,
            description="Author email for commit (optional). If omitted, uses authenticated user.",
        ),
    ) -> str:
        try:
            import json as json_lib

            files = json_lib.loads(files_json)
            data = push_files(
                oauth_token,
                owner=owner,
                repo=repo,
                files=files,
                message=message,
                branch=branch,
                author_name=author_name,
                author_email=author_email,
            )
            granted_scopes = oauth_token.scopes
            return json.dumps(
                success_response(
                    "push_files",
                    data,
                    meta={
                        "scope_check": {
                            "required": TOOL_REQUIRED_SCOPES["push_files"],
                            "granted": granted_scopes,
                            "passed": True,
                        }
                    },
                )
            )
        except GitHubServiceError as exc:
            logger.error("Failed push_files for %s/%s: %s", owner, repo, exc.message)
            return json.dumps(
                error_response(
                    "push_files",
                    code=exc.code,
                    message=exc.message,
                    http_status=exc.http_status,
                    retryable=exc.retryable,
                    details=exc.details,
                )
            )
        except Exception as exc:
            logger.error("Failed push_files for %s/%s: %s", owner, repo, exc)
            return json.dumps(
                error_response(
                    "push_files",
                    code="INTERNAL_ERROR",
                    message="Unexpected error while pushing files.",
                    details={"exception": str(exc)},
                )
            )
