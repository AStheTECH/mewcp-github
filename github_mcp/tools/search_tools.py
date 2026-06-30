import json
import logging
from fastmcp import FastMCP
from pydantic import Field

from ..schemas import ToolError, ToolResult
from ..logging_utils import ToolLogger
from ._helpers import _err, _handle_request_exc, _upstream_err
from ..service import (
    search_repositories,
    search_code,
    search_users,
    search_issues,
    search_pull_requests,
    GitHubServiceError,
)

logger = logging.getLogger("github-mcp-server")


def register_search_tools(mcp: FastMCP) -> None:

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
        tlog = ToolLogger(logger, "search_repositories")
        try:
            data = search_repositories(query, sort=sort, order=order, page=page, per_page=perPage)
            tlog.success()
            return json.dumps(ToolResult(success=True, statusCode=200, data=data).model_dump(mode="json"))
        except GitHubServiceError as exc:
            tlog.failure(exc.code, exc.message)
            return json.dumps(ToolResult(
                success=False, statusCode=exc.http_status or 400,
                error=ToolError(code=exc.code, message=exc.message, details=exc.details),
            ).model_dump(mode="json"))
        except Exception as exc:
            tlog.failure("INTERNAL_ERROR", str(exc))
            return json.dumps(ToolResult(
                success=False, statusCode=500,
                error=ToolError(code="INTERNAL_ERROR", message="Unexpected error while searching repositories.", details={"exception": str(exc)}),
            ).model_dump(mode="json"))

    @mcp.tool(
        name="search_code",
        description="Fast and precise code search across GitHub repositories.",
    )
    def search_code_tool(
        query: str = Field(..., description="Search query using GitHub code search syntax."),
        sort: str = Field("indexed", description="Sort field. Only 'indexed' is supported."),
        order: str = Field("desc", description="Sort order: asc or desc."),
        page: int = Field(1, description="Page number."),
        perPage: int = Field(30, description="Results per page (1-100)."),
    ) -> str:
        tlog = ToolLogger(logger, "search_code")
        try:
            data = search_code(query, sort=sort, order=order, page=page, per_page=perPage)
            tlog.success()
            return json.dumps(ToolResult(success=True, statusCode=200, data=data).model_dump(mode="json"))
        except GitHubServiceError as exc:
            tlog.failure(exc.code, exc.message)
            return json.dumps(ToolResult(
                success=False, statusCode=exc.http_status or 400,
                error=ToolError(code=exc.code, message=exc.message, details=exc.details),
            ).model_dump(mode="json"))
        except Exception as exc:
            tlog.failure("INTERNAL_ERROR", str(exc))
            return json.dumps(ToolResult(
                success=False, statusCode=500,
                error=ToolError(code="INTERNAL_ERROR", message="Unexpected error while searching code.", details={"exception": str(exc)}),
            ).model_dump(mode="json"))

    @mcp.tool(
        name="search_users",
        description="Search GitHub users by name, location, followers, or other attributes.",
    )
    def search_users_tool(
        query: str = Field(..., description="User search query using GitHub's search syntax."),
        sort: str = Field("followers", description="Sort field: followers, repositories, joined."),
        order: str = Field("desc", description="Sort order: asc or desc."),
        page: int = Field(1, description="Page number."),
        perPage: int = Field(30, description="Results per page (1-100)."),
    ) -> str:
        tlog = ToolLogger(logger, "search_users")
        try:
            data = search_users(query, sort=sort, order=order, page=page, per_page=perPage)
            tlog.success()
            return json.dumps(ToolResult(success=True, statusCode=200, data=data).model_dump(mode="json"))
        except GitHubServiceError as exc:
            tlog.failure(exc.code, exc.message)
            return json.dumps(ToolResult(
                success=False, statusCode=exc.http_status or 400,
                error=ToolError(code=exc.code, message=exc.message, details=exc.details),
            ).model_dump(mode="json"))
        except Exception as exc:
            tlog.failure("INTERNAL_ERROR", str(exc))
            return json.dumps(ToolResult(
                success=False, statusCode=500,
                error=ToolError(code="INTERNAL_ERROR", message="Unexpected error while searching users.", details={"exception": str(exc)}),
            ).model_dump(mode="json"))

    @mcp.tool(
        name="search_issues",
        description="Search issues and pull requests across GitHub.",
    )
    def search_issues_tool(
        query: str = Field(..., description="Search query using GitHub issue search syntax."),
        sort: str = Field("updated", description="Sort field: updated, created, comments."),
        order: str = Field("desc", description="Sort order: asc or desc."),
        owner: str | None = Field(None, description="Repository owner (optional)."),
        repo: str | None = Field(None, description="Repository name (optional)."),
        page: int = Field(1, description="Page number."),
        perPage: int = Field(30, description="Results per page (1-100)."),
    ) -> str:
        tlog = ToolLogger(logger, "search_issues")
        try:
            data = search_issues(query, sort=sort, order=order, owner=owner, repo=repo, page=page, per_page=perPage)
            tlog.success()
            return json.dumps(ToolResult(success=True, statusCode=200, data=data).model_dump(mode="json"))
        except GitHubServiceError as exc:
            tlog.failure(exc.code, exc.message)
            return json.dumps(ToolResult(
                success=False, statusCode=exc.http_status or 400,
                error=ToolError(code=exc.code, message=exc.message, details=exc.details),
            ).model_dump(mode="json"))
        except Exception as exc:
            tlog.failure("INTERNAL_ERROR", str(exc))
            return json.dumps(ToolResult(
                success=False, statusCode=500,
                error=ToolError(code="INTERNAL_ERROR", message="Unexpected error while searching issues.", details={"exception": str(exc)}),
            ).model_dump(mode="json"))

    @mcp.tool(
        name="search_pull_requests",
        description="Search for pull requests across GitHub using search syntax.",
    )
    def search_prs(
        query: str = Field(..., description="Search query using GitHub search syntax."),
        sort: str = Field("updated", description="Sort field: updated, created, comments."),
        order: str = Field("desc", description="Sort order: asc or desc."),
        owner: str | None = Field(None, description="Repository owner (optional)."),
        repo: str | None = Field(None, description="Repository name (optional)."),
        page: int = Field(1, description="Page number."),
        per_page: int = Field(30, description="Results per page."),
    ) -> str:
        tlog = ToolLogger(logger, "search_pull_requests")
        try:
            result = search_pull_requests(query=query, sort=sort, order=order, owner=owner, repo=repo, page=page, per_page=per_page)
            tlog.success()
            return json.dumps(ToolResult(success=True, statusCode=200, data=result).model_dump(mode="json"))
        except GitHubServiceError as exc:
            tlog.failure(exc.code, exc.message)
            return json.dumps(ToolResult(
                success=False, statusCode=exc.http_status or 400,
                error=ToolError(code=exc.code, message=exc.message, details=exc.details),
            ).model_dump(mode="json"))
        except Exception as exc:
            tlog.failure("INTERNAL_ERROR", str(exc))
            return json.dumps(ToolResult(
                success=False, statusCode=500,
                error=ToolError(code="INTERNAL_ERROR", message="Unexpected error while searching pull requests.", details={"exception": str(exc)}),
            ).model_dump(mode="json"))
