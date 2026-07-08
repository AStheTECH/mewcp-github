import logging
from fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from ..schemas import (
    SearchRepositoriesResult,
    SearchRepositoriesData,
    SearchCodeResult,
    SearchCodeData,
    SearchUsersResult,
    SearchUsersData,
    SearchIssuesResult,
    SearchIssuesData,
    SearchPullRequestsResult,
    SearchPullRequestsData,
)
from ..logging_utils import ToolLogger
from ._helpers import _err, _handle_service_exc
from ..service import (
    search_repositories,
    search_code,
    search_users,
    search_issues,
    search_pull_requests,
)

logger = logging.getLogger("github-mcp-server")


def register_search_tools(mcp: FastMCP) -> None:

    @mcp.tool(
        name="search_repositories",
        description="Search GitHub repositories.",
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True),
    )
    def search_repositories_tool(
        query: str = Field(..., description="Search query"),
        sort: str = Field("stars", description="Sort by: stars, forks, updated"),
        order: str = Field("desc", description="Order: asc or desc"),
        page: int = Field(1, description="Page number"),
        perPage: int = Field(30, description="Items per page"),
    ) -> SearchRepositoriesResult:
        tlog = ToolLogger(logger, "search_repositories")
        try:
            data = search_repositories(query, sort=sort, order=order, page=page, per_page=perPage)
            tlog.success()
            return SearchRepositoriesResult(success=True, statusCode=200, data=SearchRepositoriesData(**data))
        except Exception as exc:
            return _handle_service_exc(SearchRepositoriesResult, tlog, exc)

    @mcp.tool(
        name="search_code",
        description="Fast and precise code search across GitHub repositories.",
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True),
    )
    def search_code_tool(
        query: str = Field(..., description="Search query using GitHub code search syntax."),
        sort: str = Field("indexed", description="Sort field. Only 'indexed' is supported."),
        order: str = Field("desc", description="Sort order: asc or desc."),
        page: int = Field(1, description="Page number."),
        perPage: int = Field(30, description="Results per page (1-100)."),
    ) -> SearchCodeResult:
        tlog = ToolLogger(logger, "search_code")
        try:
            data = search_code(query, sort=sort, order=order, page=page, per_page=perPage)
            tlog.success()
            return SearchCodeResult(success=True, statusCode=200, data=SearchCodeData(**data))
        except Exception as exc:
            return _handle_service_exc(SearchCodeResult, tlog, exc)

    @mcp.tool(
        name="search_users",
        description="Search GitHub users by name, location, followers, or other attributes.",
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True),
    )
    def search_users_tool(
        query: str = Field(..., description="User search query using GitHub's search syntax."),
        sort: str = Field("followers", description="Sort field: followers, repositories, joined."),
        order: str = Field("desc", description="Sort order: asc or desc."),
        page: int = Field(1, description="Page number."),
        perPage: int = Field(30, description="Results per page (1-100)."),
    ) -> SearchUsersResult:
        tlog = ToolLogger(logger, "search_users")
        try:
            data = search_users(query, sort=sort, order=order, page=page, per_page=perPage)
            tlog.success()
            return SearchUsersResult(success=True, statusCode=200, data=SearchUsersData(**data))
        except Exception as exc:
            return _handle_service_exc(SearchUsersResult, tlog, exc)

    @mcp.tool(
        name="search_issues",
        description="Search issues and pull requests across GitHub.",
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True),
    )
    def search_issues_tool(
        query: str = Field(..., description="Search query using GitHub issue search syntax."),
        sort: str = Field("updated", description="Sort field: updated, created, comments."),
        order: str = Field("desc", description="Sort order: asc or desc."),
        owner: str | None = Field(None, description="Repository owner (optional)."),
        repo: str | None = Field(None, description="Repository name (optional)."),
        page: int = Field(1, description="Page number."),
        perPage: int = Field(30, description="Results per page (1-100)."),
    ) -> SearchIssuesResult:
        tlog = ToolLogger(logger, "search_issues")
        try:
            data = search_issues(query, sort=sort, order=order, owner=owner, repo=repo, page=page, per_page=perPage)
            tlog.success()
            return SearchIssuesResult(success=True, statusCode=200, data=SearchIssuesData(**data))
        except Exception as exc:
            return _handle_service_exc(SearchIssuesResult, tlog, exc)

    @mcp.tool(
        name="search_pull_requests",
        description="Search for pull requests across GitHub using search syntax.",
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True),
    )
    def search_prs(
        query: str = Field(..., description="Search query using GitHub search syntax."),
        sort: str = Field("updated", description="Sort field: updated, created, comments."),
        order: str = Field("desc", description="Sort order: asc or desc."),
        owner: str | None = Field(None, description="Repository owner (optional)."),
        repo: str | None = Field(None, description="Repository name (optional)."),
        page: int = Field(1, description="Page number."),
        per_page: int = Field(30, description="Results per page."),
    ) -> SearchPullRequestsResult:
        tlog = ToolLogger(logger, "search_pull_requests")
        try:
            result = search_pull_requests(query=query, sort=sort, order=order, owner=owner, repo=repo, page=page, per_page=per_page)
            tlog.success()
            return SearchPullRequestsResult(success=True, statusCode=200, data=SearchPullRequestsData(**result))
        except Exception as exc:
            return _handle_service_exc(SearchPullRequestsResult, tlog, exc)
