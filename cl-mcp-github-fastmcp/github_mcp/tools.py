import json
import logging

from fastmcp import FastMCP
from pydantic import Field

from .config import TOOL_REQUIRED_SCOPES
from .response import error_response, success_response
from .schemas import GitHubTokenData
from .service import (
    GitHubServiceError,
    get_file_contents,
    get_commit,
    get_repo as get_repo_service,
    list_branches,
    list_commits,
    list_issues,
    list_org_repositories_by_contributor,
    search_repositories,
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
            ..., description="GitHub token input with token and optional scopes"
        ),
        owner: str = Field(..., description="Repository owner, for example octocat"),
        repo: str = Field(..., description="Repository name"),
    ) -> str:
        try:
            result = get_repo_service(oauth_token, owner, repo)
            granted_scopes = oauth_token.get("scopes", [])
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
            granted_scopes = oauth_token.get("scopes", [])
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
            granted_scopes = oauth_token.get("scopes", [])
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
            granted_scopes = oauth_token.get("scopes", [])
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
            granted_scopes = oauth_token.get("scopes", [])
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
            granted_scopes = oauth_token.get("scopes", [])
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
            granted_scopes = oauth_token.get("scopes", [])
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
            granted_scopes = oauth_token.get("scopes", [])
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
