import json
import logging

from fastmcp import FastMCP
from pydantic import Field
from .response import error_response, success_response
from .service import (
    GitHubServiceError,
    add_issue_comment,
    add_reply_to_pull_request_comment,
    assign_copilot_to_issue,
    create_branch,
    request_copilot_review,
    create_issue,
    create_or_update_file,
    create_pull_request,
    create_repository,
    fork_repository,
    get_file_contents,
    get_commit,
    get_issue,
    get_issue_comments,
    get_label,
    get_latest_release,
    get_me,
    get_release_by_tag,
    get_repo as get_repo_service,
    get_tag,
    list_branches,
    update_repository,
    list_commits,
    list_issues,
    list_org_repositories_by_contributor,
    list_pull_requests,
    list_releases,
    list_tags,
    merge_pull_request,
    pull_request_read,
    pull_request_review_write,
    push_files,
    search_repositories,
    search_code,
    search_pull_requests,
    search_users,
    search_issues,
    sub_issue_write,
    update_issue,
    update_pull_request,
    update_pull_request_branch,
    get_branch_protection,
    set_branch_protection,
    delete_branch_protection,
    get_pull_request_review_protection,
    update_pull_request_review_protection,
    delete_pull_request_review_protection,
    list_repository_rulesets,
    get_repository_ruleset,
    create_repository_ruleset,
    update_repository_ruleset,
    delete_repository_ruleset,
)

logger = logging.getLogger("github-mcp-server")


def register_tools(mcp: FastMCP) -> None:

    @mcp.tool(
        name="get_repo",
        description="Get basic details for a GitHub repository.",
    )
    def get_repo(
        owner: str = Field(..., description="Repository owner, for example octocat"),
        repo: str = Field(..., description="Repository name"),
    ) -> str:
        try:
            result = get_repo_service(owner, repo)
            return json.dumps(
                success_response(
                    "get_repo",
                    result,
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
        name="update_repository",
        description="Update repository metadata or rename a repository.",
    )
    def update_repository_tool(
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        name: str | None = Field(None, description="New repository name (to rename)"),
        description: str | None = Field(None, description="Repository description"),
        private: bool | None = Field(
            None, description="Make repository private/public"
        ),
        default_branch: str | None = Field(None, description="Default branch name"),
    ) -> str:
        try:
            data = update_repository(
                owner=owner,
                repo=repo,
                name=name,
                description=description,
                private=private,
                default_branch=default_branch,
            )
            return json.dumps(
                success_response(
                    "update_repository",
                    data,
                )
            )
        except GitHubServiceError as exc:
            logger.error(
                "Failed update_repository for %s/%s: %s", owner, repo, exc.message
            )
            return json.dumps(
                error_response(
                    "update_repository",
                    code=exc.code,
                    message=exc.message,
                    http_status=exc.http_status,
                    retryable=exc.retryable,
                    details=exc.details,
                )
            )
        except Exception as exc:
            logger.error("Failed update_repository for %s/%s: %s", owner, repo, exc)
            return json.dumps(
                error_response(
                    "update_repository",
                    code="INTERNAL_ERROR",
                    message="Unexpected error while updating repository.",
                    details={"exception": str(exc)},
                )
            )

    @mcp.tool(
        name="list_branches",
        description="List branches in a GitHub repository.",
    )
    def list_branches_tool(
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        page: int = Field(1, description="Page number"),
        perPage: int = Field(30, description="Items per page"),
    ) -> str:
        try:
            data = list_branches(owner, repo, page=page, per_page=perPage)
            return json.dumps(
                success_response(
                    "list_branches",
                    data,
                    meta={
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
        query: str = Field(..., description="Search query"),
        sort: str = Field("stars", description="Sort by: stars, forks, updated"),
        order: str = Field("desc", description="Order: asc or desc"),
        page: int = Field(1, description="Page number"),
        perPage: int = Field(30, description="Items per page"),
    ) -> str:
        try:
            data = search_repositories(
                query, sort=sort, order=order, page=page, per_page=perPage
            )
            return json.dumps(
                success_response(
                    "search_repositories",
                    data,
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
            return json.dumps(
                success_response(
                    "list_commits",
                    data,
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
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        sha: str = Field(..., description="Commit SHA"),
        include_diff: bool = Field(True, description="Include file changes in diff"),
    ) -> str:
        try:
            data = get_commit(owner, repo, sha, include_diff=include_diff)
            return json.dumps(
                success_response(
                    "get_commit",
                    data,
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
                owner,
                repo,
                state=state,
                labels=labels,
                page=page,
                per_page=perPage,
            )
            return json.dumps(
                success_response(
                    "list_issues",
                    data,
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
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        path: str = Field("/", description="File or directory path"),
        ref: str | None = Field(None, description="Branch, tag, or commit SHA"),
    ) -> str:
        try:
            data = get_file_contents(owner, repo, path=path, ref=ref)
            return json.dumps(
                success_response(
                    "get_file_contents",
                    data,
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
                query, sort=sort, order=order, page=page, per_page=perPage
            )
            return json.dumps(
                success_response(
                    "search_code",
                    data,
                    meta={
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
                query, sort=sort, order=order, page=page, per_page=perPage
            )
            return json.dumps(
                success_response(
                    "search_users",
                    data,
                    meta={
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
                query,
                sort=sort,
                order=order,
                owner=owner,
                repo=repo,
                page=page,
                per_page=perPage,
            )
            return json.dumps(
                success_response(
                    "search_issues",
                    data,
                    meta={
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
            data = get_issue(owner, repo, issue_number)
            return json.dumps(
                success_response(
                    "get_issue",
                    data,
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
                owner, repo, issue_number, page=page, per_page=perPage
            )
            return json.dumps(
                success_response(
                    "get_issue_comments",
                    data,
                    meta={
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
                owner,
                repo,
                title,
                body=body,
                assignees=assignees,
                labels=labels,
                milestone=milestone,
            )
            return json.dumps(
                success_response(
                    "create_issue",
                    data,
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
            data = add_issue_comment(owner, repo, issue_number, body)
            return json.dumps(
                success_response(
                    "add_issue_comment",
                    data,
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
            return json.dumps(
                success_response(
                    "update_issue",
                    data,
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
                org, usernames_list, repo_type=repo_type
            )
            return json.dumps(
                success_response(
                    "list_org_repositories_by_contributor",
                    data,
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
            data = list_tags(owner, repo, page=page, per_page=perPage)
            return json.dumps(
                success_response(
                    "list_tags",
                    data,
                    meta={
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
            data = get_tag(owner, repo, tag)
            return json.dumps(
                success_response(
                    "get_tag",
                    data,
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
                name=name,
                description=description,
                private=private,
                auto_init=auto_init,
                gitignore_template=gitignore_template,
                org=org,
            )
            return json.dumps(
                success_response(
                    "create_repository",
                    data,
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
                owner=owner,
                repo=repo,
                path=path,
                content=content,
                message=message,
                branch=branch,
                sha=sha,
            )
            return json.dumps(
                success_response(
                    "create_or_update_file",
                    data,
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
        owner: str = Field(..., description="Original repository owner."),
        repo: str = Field(..., description="Original repository name."),
        org: str | None = Field(
            None,
            description="Organization name to fork into (optional). If omitted, forks to personal account.",
        ),
    ) -> str:
        try:
            data = fork_repository(owner=owner, repo=repo, org=org)
            return json.dumps(
                success_response(
                    "fork_repository",
                    data,
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
                owner=owner, repo=repo, branch_name=branch_name, sha=sha
            )
            return json.dumps(
                success_response(
                    "create_branch",
                    data,
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
                owner=owner,
                repo=repo,
                files=files,
                message=message,
                branch=branch,
                author_name=author_name,
                author_email=author_email,
            )
            return json.dumps(
                success_response(
                    "push_files",
                    data,
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

    @mcp.tool(
        name="pull_request_read",
        description="Get details for a pull request with flexible method options (get, get_files, get_status, get_comments, get_review_comments).",
    )
    def pr_read(
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        pull_number: int = Field(..., description="Pull request number"),
        method: str = Field(
            "get",
            description="Which PR data to retrieve: get, get_files, get_status, get_comments, get_review_comments",
        ),
        page: int = Field(1, description="Page number for paginated results"),
        per_page: int = Field(30, description="Results per page for paginated results"),
    ) -> str:
        try:
            result = pull_request_read(
                owner=owner,
                repo=repo,
                pull_number=pull_number,
                method=method,
                page=page,
                per_page=per_page,
            )
            return json.dumps(
                success_response(
                    "pull_request_read",
                    result,
                )
            )
        except GitHubServiceError as exc:
            logger.error(
                "Failed pull_request_read for %s/%s#%d: %s",
                owner,
                repo,
                pull_number,
                exc.message,
            )
            return json.dumps(
                error_response(
                    "pull_request_read",
                    code=exc.code,
                    message=exc.message,
                    http_status=exc.http_status,
                    retryable=exc.retryable,
                    details=exc.details,
                )
            )
        except Exception as exc:
            logger.error(
                "Failed pull_request_read for %s/%s#%d: %s",
                owner,
                repo,
                pull_number,
                exc,
            )
            return json.dumps(
                error_response(
                    "pull_request_read",
                    code="INTERNAL_ERROR",
                    message="Unexpected error while reading pull request.",
                    details={"exception": str(exc)},
                )
            )

    @mcp.tool(
        name="list_pull_requests",
        description="List pull requests in a GitHub repository with filtering and sorting options.",
    )
    def list_prs(
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        state: str = Field("open", description="Filter by state: open, closed, or all"),
        sort: str = Field(
            "created",
            description="Sort by: created, updated, popularity, or long-running",
        ),
        direction: str = Field("desc", description="Sort direction: asc or desc"),
        base: str | None = Field(None, description="Filter by base branch"),
        head: str | None = Field(
            None, description="Filter by head branch (user:branch format)"
        ),
        page: int = Field(1, description="Page number"),
        per_page: int = Field(30, description="Results per page"),
    ) -> str:
        try:
            result = list_pull_requests(
                owner=owner,
                repo=repo,
                state=state,
                sort=sort,
                direction=direction,
                base=base,
                head=head,
                page=page,
                per_page=per_page,
            )
            return json.dumps(
                success_response(
                    "list_pull_requests",
                    result,
                )
            )
        except GitHubServiceError as exc:
            logger.error(
                "Failed list_pull_requests for %s/%s: %s", owner, repo, exc.message
            )
            return json.dumps(
                error_response(
                    "list_pull_requests",
                    code=exc.code,
                    message=exc.message,
                    http_status=exc.http_status,
                    retryable=exc.retryable,
                    details=exc.details,
                )
            )
        except Exception as exc:
            logger.error("Failed list_pull_requests for %s/%s: %s", owner, repo, exc)
            return json.dumps(
                error_response(
                    "list_pull_requests",
                    code="INTERNAL_ERROR",
                    message="Unexpected error while listing pull requests.",
                    details={"exception": str(exc)},
                )
            )

    @mcp.tool(
        name="search_pull_requests",
        description="Search for pull requests across GitHub using search syntax.",
    )
    def search_prs(
        query: str = Field(..., description="Search query using GitHub search syntax"),
        sort: str = Field(
            "updated", description="Sort field: updated, created, comments, etc."
        ),
        order: str = Field("desc", description="Sort order: asc or desc"),
        owner: str | None = Field(
            None, description="Repository owner (optional with repo)"
        ),
        repo: str | None = Field(
            None, description="Repository name (optional with owner)"
        ),
        page: int = Field(1, description="Page number"),
        per_page: int = Field(30, description="Results per page"),
    ) -> str:
        try:
            result = search_pull_requests(
                query=query,
                sort=sort,
                order=order,
                owner=owner,
                repo=repo,
                page=page,
                per_page=per_page,
            )
            return json.dumps(
                success_response(
                    "search_pull_requests",
                    result,
                )
            )
        except GitHubServiceError as exc:
            logger.error("Failed search_pull_requests: %s", exc.message)
            return json.dumps(
                error_response(
                    "search_pull_requests",
                    code=exc.code,
                    message=exc.message,
                    http_status=exc.http_status,
                    retryable=exc.retryable,
                    details=exc.details,
                )
            )
        except Exception as exc:
            logger.error("Failed search_pull_requests: %s", exc)
            return json.dumps(
                error_response(
                    "search_pull_requests",
                    code="INTERNAL_ERROR",
                    message="Unexpected error while searching pull requests.",
                    details={"exception": str(exc)},
                )
            )

    @mcp.tool(
        name="create_pull_request",
        description="Create a new pull request in a GitHub repository.",
    )
    def create_pr(
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        title: str = Field(..., description="Pull request title"),
        head: str = Field(..., description="Branch containing changes"),
        base: str = Field(..., description="Branch to merge into"),
        body: str | None = Field(
            None, description="Pull request description (optional)"
        ),
        draft: bool = Field(False, description="Create as draft pull request"),
        maintainer_can_modify: bool = Field(True, description="Allow maintainer edits"),
    ) -> str:
        try:
            result = create_pull_request(
                owner=owner,
                repo=repo,
                title=title,
                head=head,
                base=base,
                body=body,
                draft=draft,
                maintainer_can_modify=maintainer_can_modify,
            )
            return json.dumps(
                success_response(
                    "create_pull_request",
                    result,
                )
            )
        except GitHubServiceError as exc:
            logger.error(
                "Failed create_pull_request for %s/%s: %s", owner, repo, exc.message
            )
            return json.dumps(
                error_response(
                    "create_pull_request",
                    code=exc.code,
                    message=exc.message,
                    http_status=exc.http_status,
                    retryable=exc.retryable,
                    details=exc.details,
                )
            )
        except Exception as exc:
            logger.error("Failed create_pull_request for %s/%s: %s", owner, repo, exc)
            return json.dumps(
                error_response(
                    "create_pull_request",
                    code="INTERNAL_ERROR",
                    message="Unexpected error while creating pull request.",
                    details={"exception": str(exc)},
                )
            )

    @mcp.tool(
        name="update_pull_request",
        description="Update an existing pull request in a GitHub repository.",
    )
    def update_pr(
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        pull_number: int = Field(..., description="Pull request number"),
        title: str | None = Field(None, description="New title (optional)"),
        body: str | None = Field(None, description="New description (optional)"),
        state: str | None = Field(None, description="'open' or 'closed' (optional)"),
        base: str | None = Field(None, description="New base branch (optional)"),
        draft: bool | None = Field(None, description="Mark as draft/ready (optional)"),
        maintainer_can_modify: bool | None = Field(
            None, description="Allow maintainer edits (optional)"
        ),
        reviewers: list[str] | None = Field(
            None, description="Request reviews from users (optional)"
        ),
    ) -> str:
        try:
            result = update_pull_request(
                owner=owner,
                repo=repo,
                pull_number=pull_number,
                title=title,
                body=body,
                state=state,
                base=base,
                draft=draft,
                maintainer_can_modify=maintainer_can_modify,
                reviewers=reviewers,
            )
            return json.dumps(
                success_response(
                    "update_pull_request",
                    result,
                )
            )
        except GitHubServiceError as exc:
            logger.error(
                "Failed update_pull_request for %s/%s#%d: %s",
                owner,
                repo,
                pull_number,
                exc.message,
            )
            return json.dumps(
                error_response(
                    "update_pull_request",
                    code=exc.code,
                    message=exc.message,
                    http_status=exc.http_status,
                    retryable=exc.retryable,
                    details=exc.details,
                )
            )
        except Exception as exc:
            logger.error(
                "Failed update_pull_request for %s/%s#%d: %s",
                owner,
                repo,
                pull_number,
                exc,
            )
            return json.dumps(
                error_response(
                    "update_pull_request",
                    code="INTERNAL_ERROR",
                    message="Unexpected error while updating pull request.",
                    details={"exception": str(exc)},
                )
            )

    @mcp.tool(
        name="merge_pull_request",
        description="Merge a pull request in a GitHub repository.",
    )
    def merge_pr(
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        pull_number: int = Field(..., description="Pull request number"),
        merge_method: str = Field(
            "merge", description="'merge', 'squash', or 'rebase'"
        ),
        commit_title: str | None = Field(
            None, description="Custom commit title (optional)"
        ),
        commit_message: str | None = Field(
            None, description="Commit message details (optional)"
        ),
    ) -> str:
        try:
            result = merge_pull_request(
                owner=owner,
                repo=repo,
                pull_number=pull_number,
                merge_method=merge_method,
                commit_title=commit_title,
                commit_message=commit_message,
            )
            return json.dumps(
                success_response(
                    "merge_pull_request",
                    result,
                )
            )
        except GitHubServiceError as exc:
            logger.error(
                "Failed merge_pull_request for %s/%s#%d: %s",
                owner,
                repo,
                pull_number,
                exc.message,
            )
            return json.dumps(
                error_response(
                    "merge_pull_request",
                    code=exc.code,
                    message=exc.message,
                    http_status=exc.http_status,
                    retryable=exc.retryable,
                    details=exc.details,
                )
            )
        except Exception as exc:
            logger.error(
                "Failed merge_pull_request for %s/%s#%d: %s",
                owner,
                repo,
                pull_number,
                exc,
            )
            return json.dumps(
                error_response(
                    "merge_pull_request",
                    code="INTERNAL_ERROR",
                    message="Unexpected error while merging pull request.",
                    details={"exception": str(exc)},
                )
            )

    @mcp.tool(
        name="update_pull_request_branch",
        description="Update pull request branch with latest changes from base branch.",
    )
    def update_pr_branch(
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        pull_number: int = Field(..., description="Pull request number"),
        expected_head_sha: str | None = Field(
            None, description="Expected HEAD SHA (optional)"
        ),
    ) -> str:
        try:
            result = update_pull_request_branch(
                owner=owner,
                repo=repo,
                pull_number=pull_number,
                expected_head_sha=expected_head_sha,
            )
            return json.dumps(
                success_response(
                    "update_pull_request_branch",
                    result,
                )
            )
        except GitHubServiceError as exc:
            logger.error(
                "Failed update_pull_request_branch for %s/%s#%d: %s",
                owner,
                repo,
                pull_number,
                exc.message,
            )
            return json.dumps(
                error_response(
                    "update_pull_request_branch",
                    code=exc.code,
                    message=exc.message,
                    http_status=exc.http_status,
                    retryable=exc.retryable,
                    details=exc.details,
                )
            )
        except Exception as exc:
            logger.error(
                "Failed update_pull_request_branch for %s/%s#%d: %s",
                owner,
                repo,
                pull_number,
                exc,
            )
            return json.dumps(
                error_response(
                    "update_pull_request_branch",
                    code="INTERNAL_ERROR",
                    message="Unexpected error while updating pull request branch.",
                    details={"exception": str(exc)},
                )
            )

    @mcp.tool(
        name="pull_request_review_write",
        description="Write operations on PR reviews (create, submit, delete, resolve/unresolve threads).",
    )
    def pr_review_write(
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        pull_number: int = Field(..., description="Pull request number"),
        method: str = Field(
            ...,
            description="create, submit_pending, delete_pending, resolve_thread, or unresolve_thread",
        ),
        commit_id: str | None = Field(
            None, description="Commit SHA (required for create)"
        ),
        body: str | None = Field(None, description="Review comment text (optional)"),
        event: str | None = Field(
            None,
            description="APPROVE, REQUEST_CHANGES, or COMMENT (optional for create, required for submit_pending)",
        ),
        thread_id: str | None = Field(
            None, description="Thread ID for thread operations"
        ),
    ) -> str:
        try:
            result = pull_request_review_write(
                owner=owner,
                repo=repo,
                pull_number=pull_number,
                method=method,
                commit_id=commit_id,
                body=body,
                event=event,
                thread_id=thread_id,
            )
            return json.dumps(
                success_response(
                    "pull_request_review_write",
                    result,
                )
            )
        except GitHubServiceError as exc:
            logger.error(
                "Failed pull_request_review_write for %s/%s#%d: %s",
                owner,
                repo,
                pull_number,
                exc.message,
            )
            return json.dumps(
                error_response(
                    "pull_request_review_write",
                    code=exc.code,
                    message=exc.message,
                    http_status=exc.http_status,
                    retryable=exc.retryable,
                    details=exc.details,
                )
            )
        except Exception as exc:
            logger.error(
                "Failed pull_request_review_write for %s/%s#%d: %s",
                owner,
                repo,
                pull_number,
                exc,
            )
            return json.dumps(
                error_response(
                    "pull_request_review_write",
                    code="INTERNAL_ERROR",
                    message="Unexpected error while writing pull request review.",
                    details={"exception": str(exc)},
                )
            )

    @mcp.tool(
        name="add_reply_to_pull_request_comment",
        description="Add a reply to an existing pull request comment.",
    )
    def add_pr_comment_reply(
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        pull_number: int = Field(..., description="Pull request number"),
        comment_id: int = Field(..., description="ID of the comment to reply to"),
        body: str = Field(..., description="Reply text"),
    ) -> str:
        try:
            result = add_reply_to_pull_request_comment(
                owner=owner,
                repo=repo,
                pull_number=pull_number,
                comment_id=comment_id,
                body=body,
            )
            return json.dumps(
                success_response(
                    "add_reply_to_pull_request_comment",
                    result,
                )
            )
        except GitHubServiceError as exc:
            logger.error(
                "Failed add_reply_to_pull_request_comment for %s/%s#%d: %s",
                owner,
                repo,
                pull_number,
                exc.message,
            )
            return json.dumps(
                error_response(
                    "add_reply_to_pull_request_comment",
                    code=exc.code,
                    message=exc.message,
                    http_status=exc.http_status,
                    retryable=exc.retryable,
                    details=exc.details,
                )
            )
        except Exception as exc:
            logger.error(
                "Failed add_reply_to_pull_request_comment for %s/%s#%d: %s",
                owner,
                repo,
                pull_number,
                exc,
            )
            return json.dumps(
                error_response(
                    "add_reply_to_pull_request_comment",
                    code="INTERNAL_ERROR",
                    message="Unexpected error while adding pull request comment reply.",
                    details={"exception": str(exc)},
                )
            )

    @mcp.tool(
        name="get_latest_release",
        description="Get the latest release of a GitHub repository.",
    )
    def get_latest_release_tool(
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
    ) -> str:
        try:
            result = get_latest_release(owner, repo)
            return json.dumps(
                success_response(
                    "get_latest_release",
                    result,
                )
            )
        except GitHubServiceError as exc:
            logger.error(
                "Failed get_latest_release for %s/%s: %s", owner, repo, exc.message
            )
            return json.dumps(
                error_response(
                    "get_latest_release",
                    code=exc.code,
                    message=exc.message,
                    http_status=exc.http_status,
                    retryable=exc.retryable,
                    details=exc.details,
                )
            )
        except Exception as exc:
            logger.error("Failed get_latest_release for %s/%s: %s", owner, repo, exc)
            return json.dumps(
                error_response(
                    "get_latest_release",
                    code="INTERNAL_ERROR",
                    message="Unexpected error while fetching latest release.",
                    details={"exception": str(exc)},
                )
            )

    @mcp.tool(
        name="list_releases",
        description="List releases in a GitHub repository.",
    )
    def list_releases_tool(
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        page: int = Field(1, description="Page number for pagination"),
        per_page: int = Field(30, description="Results per page"),
    ) -> str:
        try:
            result = list_releases(owner, repo, page, per_page)
            return json.dumps(
                success_response(
                    "list_releases",
                    result,
                )
            )
        except GitHubServiceError as exc:
            logger.error("Failed list_releases for %s/%s: %s", owner, repo, exc.message)
            return json.dumps(
                error_response(
                    "list_releases",
                    code=exc.code,
                    message=exc.message,
                    http_status=exc.http_status,
                    retryable=exc.retryable,
                    details=exc.details,
                )
            )
        except Exception as exc:
            logger.error("Failed list_releases for %s/%s: %s", owner, repo, exc)
            return json.dumps(
                error_response(
                    "list_releases",
                    code="INTERNAL_ERROR",
                    message="Unexpected error while listing releases.",
                    details={"exception": str(exc)},
                )
            )

    @mcp.tool(
        name="get_release_by_tag",
        description="Get a specific release by tag name.",
    )
    def get_release_by_tag_tool(
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        tag: str = Field(..., description="Tag name"),
    ) -> str:
        try:
            result = get_release_by_tag(owner, repo, tag)
            return json.dumps(
                success_response(
                    "get_release_by_tag",
                    result,
                )
            )
        except GitHubServiceError as exc:
            logger.error(
                "Failed get_release_by_tag for %s/%s tag %s: %s",
                owner,
                repo,
                tag,
                exc.message,
            )
            return json.dumps(
                error_response(
                    "get_release_by_tag",
                    code=exc.code,
                    message=exc.message,
                    http_status=exc.http_status,
                    retryable=exc.retryable,
                    details=exc.details,
                )
            )
        except Exception as exc:
            logger.error(
                "Failed get_release_by_tag for %s/%s tag %s: %s", owner, repo, tag, exc
            )
            return json.dumps(
                error_response(
                    "get_release_by_tag",
                    code="INTERNAL_ERROR",
                    message="Unexpected error while fetching release by tag.",
                    details={"exception": str(exc)},
                )
            )

    @mcp.tool(
        name="get_label",
        description="Get a specific label from a repository.",
    )
    def get_label_tool(
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        name: str = Field(..., description="Label name"),
    ) -> str:
        try:
            result = get_label(owner, repo, name)
            return json.dumps(
                success_response(
                    "get_label",
                    result,
                )
            )
        except GitHubServiceError as exc:
            logger.error(
                "Failed get_label for %s/%s label %s: %s",
                owner,
                repo,
                name,
                exc.message,
            )
            return json.dumps(
                error_response(
                    "get_label",
                    code=exc.code,
                    message=exc.message,
                    http_status=exc.http_status,
                    retryable=exc.retryable,
                    details=exc.details,
                )
            )
        except Exception as exc:
            logger.error(
                "Failed get_label for %s/%s label %s: %s", owner, repo, name, exc
            )
            return json.dumps(
                error_response(
                    "get_label",
                    code="INTERNAL_ERROR",
                    message="Unexpected error while fetching label.",
                    details={"exception": str(exc)},
                )
            )

    @mcp.tool(
        name="get_me",
        description="Get details of the authenticated GitHub user.",
    )
    def get_me_tool() -> str:
        try:
            result = get_me()
            return json.dumps(
                success_response(
                    "get_me",
                    result,
                )
            )
        except GitHubServiceError as exc:
            logger.error("Failed get_me: %s", exc.message)
            return json.dumps(
                error_response(
                    "get_me",
                    code=exc.code,
                    message=exc.message,
                    http_status=exc.http_status,
                    retryable=exc.retryable,
                    details=exc.details,
                )
            )
        except Exception as exc:
            logger.error("Failed get_me: %s", exc)
            return json.dumps(
                error_response(
                    "get_me",
                    code="INTERNAL_ERROR",
                    message="Unexpected error while fetching user details.",
                    details={"exception": str(exc)},
                )
            )

    @mcp.tool(
        name="sub_issue_write",
        description="Manage sub-issues for a parent issue (add, remove, reprioritize).",
    )
    def sub_issue_write_tool(
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        issue_number: int = Field(..., description="Parent issue number"),
        method: str = Field(
            ..., description="Method: 'add', 'remove', or 'reprioritize'"
        ),
        sub_issue_id: int = Field(..., description="Sub-issue ID"),
        replace_parent: bool = Field(
            False, description="Replace current parent when adding"
        ),
        after_id: int | None = Field(
            None, description="Position after this sub-issue ID"
        ),
        before_id: int | None = Field(
            None, description="Position before this sub-issue ID"
        ),
    ) -> str:
        try:
            result = sub_issue_write(
                owner,
                repo,
                issue_number,
                method,
                sub_issue_id,
                replace_parent,
                after_id,
                before_id,
            )
            return json.dumps(
                success_response(
                    "sub_issue_write",
                    result,
                )
            )
        except GitHubServiceError as exc:
            logger.error(
                "Failed sub_issue_write for %s/%s#%d: %s",
                owner,
                repo,
                issue_number,
                exc.message,
            )
            return json.dumps(
                error_response(
                    "sub_issue_write",
                    code=exc.code,
                    message=exc.message,
                    http_status=exc.http_status,
                    retryable=exc.retryable,
                    details=exc.details,
                )
            )
        except Exception as exc:
            logger.error(
                "Failed sub_issue_write for %s/%s#%d: %s",
                owner,
                repo,
                issue_number,
                exc,
            )
            return json.dumps(
                error_response(
                    "sub_issue_write",
                    code="INTERNAL_ERROR",
                    message="Unexpected error while managing sub-issues.",
                    details={"exception": str(exc)},
                )
            )

    @mcp.tool(
        name="assign_copilot_to_issue",
        description="Assign GitHub Copilot to work on an issue.",
    )
    def assign_copilot_to_issue_tool(
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        issue_number: int = Field(..., description="Issue number"),
        base_ref: str | None = Field(
            None, description="Git reference (branch) to start from"
        ),
        custom_instructions: str | None = Field(
            None, description="Custom instructions for Copilot"
        ),
    ) -> str:
        try:
            result = assign_copilot_to_issue(
                owner, repo, issue_number, base_ref, custom_instructions
            )
            return json.dumps(
                success_response(
                    "assign_copilot_to_issue",
                    result,
                )
            )
        except GitHubServiceError as exc:
            logger.error(
                "Failed assign_copilot_to_issue for %s/%s#%d: %s",
                owner,
                repo,
                issue_number,
                exc.message,
            )
            return json.dumps(
                error_response(
                    "assign_copilot_to_issue",
                    code=exc.code,
                    message=exc.message,
                    http_status=exc.http_status,
                    retryable=exc.retryable,
                    details=exc.details,
                )
            )
        except Exception as exc:
            logger.error(
                "Failed assign_copilot_to_issue for %s/%s#%d: %s",
                owner,
                repo,
                issue_number,
                exc,
            )
            return json.dumps(
                error_response(
                    "assign_copilot_to_issue",
                    code="INTERNAL_ERROR",
                    message="Unexpected error while assigning Copilot to issue.",
                    details={"exception": str(exc)},
                )
            )

    @mcp.tool(
        name="request_copilot_review",
        description="Request a code review from GitHub Copilot on a pull request.",
    )
    def request_copilot_review_tool(
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        pull_number: int = Field(..., description="Pull request number"),
    ) -> str:
        try:
            result = request_copilot_review(owner, repo, pull_number)
            return json.dumps(
                success_response(
                    "request_copilot_review",
                    result,
                )
            )
        except GitHubServiceError as exc:
            logger.error(
                "Failed request_copilot_review for %s/%s#%d: %s",
                owner,
                repo,
                pull_number,
                exc.message,
            )
            return json.dumps(
                error_response(
                    "request_copilot_review",
                    code=exc.code,
                    message=exc.message,
                    http_status=exc.http_status,
                    retryable=exc.retryable,
                    details=exc.details,
                )
            )
        except Exception as exc:
            logger.error(
                "Failed request_copilot_review for %s/%s#%d: %s",
                owner,
                repo,
                pull_number,
                exc,
            )
            return json.dumps(
                error_response(
                    "request_copilot_review",
                    code="INTERNAL_ERROR",
                    message="Unexpected error while requesting Copilot review.",
                    details={"exception": str(exc)},
                )
            )

    # ── Branch Protection ──────────────────────────────────────────────────────

    @mcp.tool(
        name="get_branch_protection",
        description="Get branch protection rules for a specific branch.",
    )
    def get_branch_protection_tool(
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        branch: str = Field(..., description="Branch name"),
    ) -> str:
        try:
            data = get_branch_protection(owner, repo, branch)
            return json.dumps(success_response("get_branch_protection", data))
        except GitHubServiceError as exc:
            logger.error(
                "Failed get_branch_protection for %s/%s:%s: %s",
                owner, repo, branch, exc.message,
            )
            return json.dumps(
                error_response(
                    "get_branch_protection",
                    code=exc.code,
                    message=exc.message,
                    http_status=exc.http_status,
                    retryable=exc.retryable,
                    details=exc.details,
                )
            )
        except Exception as exc:
            logger.error(
                "Failed get_branch_protection for %s/%s:%s: %s",
                owner, repo, branch, exc,
            )
            return json.dumps(
                error_response(
                    "get_branch_protection",
                    code="INTERNAL_ERROR",
                    message="Unexpected error while getting branch protection.",
                    details={"exception": str(exc)},
                )
            )

    @mcp.tool(
        name="set_branch_protection",
        description=(
            "Create or replace branch protection rules for a branch (PUT). "
            "Pass complex nested objects (required_status_checks, required_pull_request_reviews, restrictions) "
            "as JSON strings; set to 'null' (the string) to clear them."
        ),
    )
    def set_branch_protection_tool(
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        branch: str = Field(..., description="Branch name to protect"),
        enforce_admins: bool = Field(
            ..., description="Enforce rules for administrators"
        ),
        required_status_checks_json: str | None = Field(
            None,
            description=(
                'JSON string for required status checks or null to disable. '
                'Example: \'{"strict": true, "contexts": ["ci/test"]}\''
            ),
        ),
        required_pull_request_reviews_json: str | None = Field(
            None,
            description=(
                'JSON string for PR review requirements or null to disable. '
                'Example: \'{"required_approving_review_count": 1, "dismiss_stale_reviews": true, '
                '"require_code_owner_reviews": false, "require_last_push_approval": false}\''
            ),
        ),
        restrictions_json: str | None = Field(
            None,
            description=(
                'JSON string restricting push access or null for no restrictions. '
                'Example: \'{"users": ["octocat"], "teams": ["ops"], "apps": []}\''
            ),
        ),
        required_linear_history: bool = Field(
            False, description="Require linear commit history"
        ),
        allow_force_pushes: bool | None = Field(
            None, description="Allow force pushes (null uses GitHub default)"
        ),
        allow_deletions: bool = Field(False, description="Allow branch deletion"),
        block_creations: bool = Field(
            False, description="Block matching ref creation"
        ),
        required_conversation_resolution: bool = Field(
            False, description="Require all conversations resolved before merge"
        ),
        lock_branch: bool = Field(False, description="Mark branch as read-only"),
        allow_fork_syncing: bool = Field(
            False, description="Allow forks to sync with upstream"
        ),
    ) -> str:
        try:
            import json as _json

            required_status_checks = (
                _json.loads(required_status_checks_json)
                if required_status_checks_json
                else None
            )
            required_pull_request_reviews = (
                _json.loads(required_pull_request_reviews_json)
                if required_pull_request_reviews_json
                else None
            )
            restrictions = (
                _json.loads(restrictions_json) if restrictions_json else None
            )

            data = set_branch_protection(
                owner=owner,
                repo=repo,
                branch=branch,
                enforce_admins=enforce_admins,
                required_status_checks=required_status_checks,
                required_pull_request_reviews=required_pull_request_reviews,
                restrictions=restrictions,
                required_linear_history=required_linear_history,
                allow_force_pushes=allow_force_pushes,
                allow_deletions=allow_deletions,
                block_creations=block_creations,
                required_conversation_resolution=required_conversation_resolution,
                lock_branch=lock_branch,
                allow_fork_syncing=allow_fork_syncing,
            )
            return json.dumps(success_response("set_branch_protection", data))
        except GitHubServiceError as exc:
            logger.error(
                "Failed set_branch_protection for %s/%s:%s: %s",
                owner, repo, branch, exc.message,
            )
            return json.dumps(
                error_response(
                    "set_branch_protection",
                    code=exc.code,
                    message=exc.message,
                    http_status=exc.http_status,
                    retryable=exc.retryable,
                    details=exc.details,
                )
            )
        except Exception as exc:
            logger.error(
                "Failed set_branch_protection for %s/%s:%s: %s",
                owner, repo, branch, exc,
            )
            return json.dumps(
                error_response(
                    "set_branch_protection",
                    code="INTERNAL_ERROR",
                    message="Unexpected error while setting branch protection.",
                    details={"exception": str(exc)},
                )
            )

    @mcp.tool(
        name="delete_branch_protection",
        description="Delete all branch protection rules for a specific branch.",
    )
    def delete_branch_protection_tool(
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        branch: str = Field(..., description="Branch name"),
    ) -> str:
        try:
            data = delete_branch_protection(owner, repo, branch)
            return json.dumps(success_response("delete_branch_protection", data))
        except GitHubServiceError as exc:
            logger.error(
                "Failed delete_branch_protection for %s/%s:%s: %s",
                owner, repo, branch, exc.message,
            )
            return json.dumps(
                error_response(
                    "delete_branch_protection",
                    code=exc.code,
                    message=exc.message,
                    http_status=exc.http_status,
                    retryable=exc.retryable,
                    details=exc.details,
                )
            )
        except Exception as exc:
            logger.error(
                "Failed delete_branch_protection for %s/%s:%s: %s",
                owner, repo, branch, exc,
            )
            return json.dumps(
                error_response(
                    "delete_branch_protection",
                    code="INTERNAL_ERROR",
                    message="Unexpected error while deleting branch protection.",
                    details={"exception": str(exc)},
                )
            )

    @mcp.tool(
        name="get_pull_request_review_protection",
        description="Get the PR review requirements for a protected branch.",
    )
    def get_pr_review_protection_tool(
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        branch: str = Field(..., description="Branch name"),
    ) -> str:
        try:
            data = get_pull_request_review_protection(owner, repo, branch)
            return json.dumps(
                success_response("get_pull_request_review_protection", data)
            )
        except GitHubServiceError as exc:
            logger.error(
                "Failed get_pull_request_review_protection for %s/%s:%s: %s",
                owner, repo, branch, exc.message,
            )
            return json.dumps(
                error_response(
                    "get_pull_request_review_protection",
                    code=exc.code,
                    message=exc.message,
                    http_status=exc.http_status,
                    retryable=exc.retryable,
                    details=exc.details,
                )
            )
        except Exception as exc:
            logger.error(
                "Failed get_pull_request_review_protection for %s/%s:%s: %s",
                owner, repo, branch, exc,
            )
            return json.dumps(
                error_response(
                    "get_pull_request_review_protection",
                    code="INTERNAL_ERROR",
                    message="Unexpected error while getting PR review protection.",
                    details={"exception": str(exc)},
                )
            )

    @mcp.tool(
        name="update_pull_request_review_protection",
        description=(
            "Update PR review requirements for a protected branch (PATCH). "
            "Only provided fields are updated."
        ),
    )
    def update_pr_review_protection_tool(
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        branch: str = Field(..., description="Branch name"),
        dismiss_stale_reviews: bool | None = Field(
            None,
            description="Dismiss approved reviews when new commits are pushed",
        ),
        require_code_owner_reviews: bool | None = Field(
            None, description="Require review from code owners"
        ),
        required_approving_review_count: int | None = Field(
            None, description="Number of approvals required (0–6)"
        ),
        require_last_push_approval: bool | None = Field(
            None,
            description="Require approval from someone other than the last pusher",
        ),
        dismissal_restrictions_json: str | None = Field(
            None,
            description=(
                'JSON string specifying who can dismiss stale reviews. '
                'Example: \'{"users": ["octocat"], "teams": ["ops"]}\''
            ),
        ),
    ) -> str:
        try:
            import json as _json

            dismissal_restrictions = (
                _json.loads(dismissal_restrictions_json)
                if dismissal_restrictions_json
                else None
            )

            data = update_pull_request_review_protection(
                owner=owner,
                repo=repo,
                branch=branch,
                dismiss_stale_reviews=dismiss_stale_reviews,
                require_code_owner_reviews=require_code_owner_reviews,
                required_approving_review_count=required_approving_review_count,
                require_last_push_approval=require_last_push_approval,
                dismissal_restrictions=dismissal_restrictions,
            )
            return json.dumps(
                success_response("update_pull_request_review_protection", data)
            )
        except GitHubServiceError as exc:
            logger.error(
                "Failed update_pull_request_review_protection for %s/%s:%s: %s",
                owner, repo, branch, exc.message,
            )
            return json.dumps(
                error_response(
                    "update_pull_request_review_protection",
                    code=exc.code,
                    message=exc.message,
                    http_status=exc.http_status,
                    retryable=exc.retryable,
                    details=exc.details,
                )
            )
        except Exception as exc:
            logger.error(
                "Failed update_pull_request_review_protection for %s/%s:%s: %s",
                owner, repo, branch, exc,
            )
            return json.dumps(
                error_response(
                    "update_pull_request_review_protection",
                    code="INTERNAL_ERROR",
                    message="Unexpected error while updating PR review protection.",
                    details={"exception": str(exc)},
                )
            )

    @mcp.tool(
        name="delete_pull_request_review_protection",
        description="Remove PR review requirements from a protected branch.",
    )
    def delete_pr_review_protection_tool(
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        branch: str = Field(..., description="Branch name"),
    ) -> str:
        try:
            data = delete_pull_request_review_protection(owner, repo, branch)
            return json.dumps(
                success_response("delete_pull_request_review_protection", data)
            )
        except GitHubServiceError as exc:
            logger.error(
                "Failed delete_pull_request_review_protection for %s/%s:%s: %s",
                owner, repo, branch, exc.message,
            )
            return json.dumps(
                error_response(
                    "delete_pull_request_review_protection",
                    code=exc.code,
                    message=exc.message,
                    http_status=exc.http_status,
                    retryable=exc.retryable,
                    details=exc.details,
                )
            )
        except Exception as exc:
            logger.error(
                "Failed delete_pull_request_review_protection for %s/%s:%s: %s",
                owner, repo, branch, exc,
            )
            return json.dumps(
                error_response(
                    "delete_pull_request_review_protection",
                    code="INTERNAL_ERROR",
                    message="Unexpected error while deleting PR review protection.",
                    details={"exception": str(exc)},
                )
            )

    # ── Repository Rulesets ────────────────────────────────────────────────────

    @mcp.tool(
        name="list_repository_rulesets",
        description="List all rulesets defined for a repository.",
    )
    def list_repository_rulesets_tool(
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        includes_parents: bool = Field(
            True,
            description="Include rulesets inherited from the parent organization",
        ),
        page: int = Field(1, description="Page number"),
        perPage: int = Field(30, description="Items per page"),
    ) -> str:
        try:
            data = list_repository_rulesets(
                owner, repo, includes_parents=includes_parents, per_page=perPage, page=page
            )
            return json.dumps(
                success_response(
                    "list_repository_rulesets",
                    data,
                    meta={"pagination": {"page": page, "perPage": perPage}},
                )
            )
        except GitHubServiceError as exc:
            logger.error(
                "Failed list_repository_rulesets for %s/%s: %s",
                owner, repo, exc.message,
            )
            return json.dumps(
                error_response(
                    "list_repository_rulesets",
                    code=exc.code,
                    message=exc.message,
                    http_status=exc.http_status,
                    retryable=exc.retryable,
                    details=exc.details,
                )
            )
        except Exception as exc:
            logger.error(
                "Failed list_repository_rulesets for %s/%s: %s", owner, repo, exc
            )
            return json.dumps(
                error_response(
                    "list_repository_rulesets",
                    code="INTERNAL_ERROR",
                    message="Unexpected error while listing rulesets.",
                    details={"exception": str(exc)},
                )
            )

    @mcp.tool(
        name="get_repository_ruleset",
        description="Get a specific ruleset by ID for a repository.",
    )
    def get_repository_ruleset_tool(
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        ruleset_id: int = Field(..., description="Ruleset ID"),
    ) -> str:
        try:
            data = get_repository_ruleset(owner, repo, ruleset_id)
            return json.dumps(success_response("get_repository_ruleset", data))
        except GitHubServiceError as exc:
            logger.error(
                "Failed get_repository_ruleset for %s/%s#%d: %s",
                owner, repo, ruleset_id, exc.message,
            )
            return json.dumps(
                error_response(
                    "get_repository_ruleset",
                    code=exc.code,
                    message=exc.message,
                    http_status=exc.http_status,
                    retryable=exc.retryable,
                    details=exc.details,
                )
            )
        except Exception as exc:
            logger.error(
                "Failed get_repository_ruleset for %s/%s#%d: %s",
                owner, repo, ruleset_id, exc,
            )
            return json.dumps(
                error_response(
                    "get_repository_ruleset",
                    code="INTERNAL_ERROR",
                    message="Unexpected error while getting ruleset.",
                    details={"exception": str(exc)},
                )
            )

    @mcp.tool(
        name="create_repository_ruleset",
        description=(
            "Create a new ruleset for a repository. "
            "Pass conditions, rules, and bypass_actors as JSON strings."
        ),
    )
    def create_repository_ruleset_tool(
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        name: str = Field(..., description="Ruleset name"),
        enforcement: str = Field(
            ..., description="Enforcement level: active, evaluate, or disabled"
        ),
        target: str = Field(
            "branch", description="Target type: branch, tag, or push"
        ),
        conditions_json: str | None = Field(
            None,
            description=(
                'JSON string for ref conditions. '
                'Example: \'{"ref_name": {"include": ["~DEFAULT_BRANCH"], "exclude": []}}\''
            ),
        ),
        rules_json: str | None = Field(
            None,
            description=(
                'JSON array of rule objects. '
                'Example: \'[{"type": "pull_request", "parameters": {"required_approving_review_count": 1}}]\''
            ),
        ),
        bypass_actors_json: str | None = Field(
            None,
            description=(
                'JSON array of bypass actor objects. '
                'Example: \'[{"actor_id": 1, "actor_type": "Team", "bypass_mode": "always"}]\''
            ),
        ),
    ) -> str:
        try:
            import json as _json

            conditions = _json.loads(conditions_json) if conditions_json else None
            rules = _json.loads(rules_json) if rules_json else None
            bypass_actors = (
                _json.loads(bypass_actors_json) if bypass_actors_json else None
            )

            data = create_repository_ruleset(
                owner=owner,
                repo=repo,
                name=name,
                enforcement=enforcement,
                target=target,
                conditions=conditions,
                rules=rules,
                bypass_actors=bypass_actors,
            )
            return json.dumps(success_response("create_repository_ruleset", data))
        except GitHubServiceError as exc:
            logger.error(
                "Failed create_repository_ruleset for %s/%s: %s",
                owner, repo, exc.message,
            )
            return json.dumps(
                error_response(
                    "create_repository_ruleset",
                    code=exc.code,
                    message=exc.message,
                    http_status=exc.http_status,
                    retryable=exc.retryable,
                    details=exc.details,
                )
            )
        except Exception as exc:
            logger.error(
                "Failed create_repository_ruleset for %s/%s: %s", owner, repo, exc
            )
            return json.dumps(
                error_response(
                    "create_repository_ruleset",
                    code="INTERNAL_ERROR",
                    message="Unexpected error while creating ruleset.",
                    details={"exception": str(exc)},
                )
            )

    @mcp.tool(
        name="update_repository_ruleset",
        description=(
            "Update an existing ruleset for a repository (PUT — replaces the full ruleset). "
            "Pass conditions, rules, and bypass_actors as JSON strings."
        ),
    )
    def update_repository_ruleset_tool(
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        ruleset_id: int = Field(..., description="Ruleset ID to update"),
        name: str | None = Field(None, description="New ruleset name"),
        enforcement: str | None = Field(
            None, description="Enforcement level: active, evaluate, or disabled"
        ),
        target: str | None = Field(
            None, description="Target type: branch, tag, or push"
        ),
        conditions_json: str | None = Field(
            None,
            description=(
                'JSON string for ref conditions. '
                'Example: \'{"ref_name": {"include": ["~DEFAULT_BRANCH"], "exclude": []}}\''
            ),
        ),
        rules_json: str | None = Field(
            None,
            description=(
                'JSON array of rule objects. '
                'Example: \'[{"type": "pull_request", "parameters": {"required_approving_review_count": 2}}]\''
            ),
        ),
        bypass_actors_json: str | None = Field(
            None,
            description=(
                'JSON array of bypass actor objects. '
                'Example: \'[{"actor_id": 1, "actor_type": "Team", "bypass_mode": "always"}]\''
            ),
        ),
    ) -> str:
        try:
            import json as _json

            conditions = _json.loads(conditions_json) if conditions_json else None
            rules = _json.loads(rules_json) if rules_json else None
            bypass_actors = (
                _json.loads(bypass_actors_json) if bypass_actors_json else None
            )

            data = update_repository_ruleset(
                owner=owner,
                repo=repo,
                ruleset_id=ruleset_id,
                name=name,
                enforcement=enforcement,
                target=target,
                conditions=conditions,
                rules=rules,
                bypass_actors=bypass_actors,
            )
            return json.dumps(success_response("update_repository_ruleset", data))
        except GitHubServiceError as exc:
            logger.error(
                "Failed update_repository_ruleset for %s/%s#%d: %s",
                owner, repo, ruleset_id, exc.message,
            )
            return json.dumps(
                error_response(
                    "update_repository_ruleset",
                    code=exc.code,
                    message=exc.message,
                    http_status=exc.http_status,
                    retryable=exc.retryable,
                    details=exc.details,
                )
            )
        except Exception as exc:
            logger.error(
                "Failed update_repository_ruleset for %s/%s#%d: %s",
                owner, repo, ruleset_id, exc,
            )
            return json.dumps(
                error_response(
                    "update_repository_ruleset",
                    code="INTERNAL_ERROR",
                    message="Unexpected error while updating ruleset.",
                    details={"exception": str(exc)},
                )
            )

    @mcp.tool(
        name="delete_repository_ruleset",
        description="Delete a ruleset from a repository by its ID.",
    )
    def delete_repository_ruleset_tool(
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        ruleset_id: int = Field(..., description="Ruleset ID to delete"),
    ) -> str:
        try:
            data = delete_repository_ruleset(owner, repo, ruleset_id)
            return json.dumps(success_response("delete_repository_ruleset", data))
        except GitHubServiceError as exc:
            logger.error(
                "Failed delete_repository_ruleset for %s/%s#%d: %s",
                owner, repo, ruleset_id, exc.message,
            )
            return json.dumps(
                error_response(
                    "delete_repository_ruleset",
                    code=exc.code,
                    message=exc.message,
                    http_status=exc.http_status,
                    retryable=exc.retryable,
                    details=exc.details,
                )
            )
        except Exception as exc:
            logger.error(
                "Failed delete_repository_ruleset for %s/%s#%d: %s",
                owner, repo, ruleset_id, exc,
            )
            return json.dumps(
                error_response(
                    "delete_repository_ruleset",
                    code="INTERNAL_ERROR",
                    message="Unexpected error while deleting ruleset.",
                    details={"exception": str(exc)},
                )
            )
