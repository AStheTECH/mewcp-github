import json
import logging
from fastmcp import FastMCP
from pydantic import Field

from ..schemas import ToolError, ToolResult
from ..logging_utils import ToolLogger
from ._helpers import _err, _handle_request_exc, _upstream_err
from ..service import (
    list_issues,
    get_issue,
    get_issue_comments,
    create_issue,
    add_issue_comment,
    update_issue,
    list_org_repositories_by_contributor,
    sub_issue_write,
    assign_copilot_to_issue,
    GitHubServiceError,
)

logger = logging.getLogger("github-mcp-server")


def register_issue_tools(mcp: FastMCP) -> None:

    @mcp.tool(
        name="list_issues",
        description="List issues in a GitHub repository.",
    )
    def list_issues_tool(
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        state: str = Field("open", description="Filter by state: open, closed, all"),
        labels: str | None = Field(None, description="Comma-separated label names to filter by"),
        page: int = Field(1, description="Page number"),
        perPage: int = Field(30, description="Items per page"),
    ) -> str:
        tlog = ToolLogger(logger, "list_issues")
        try:
            data = list_issues(owner, repo, state=state, labels=labels, page=page, per_page=perPage)
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
                error=ToolError(code="INTERNAL_ERROR", message="Unexpected error while listing issues.", details={"exception": str(exc)}),
            ).model_dump(mode="json"))

    @mcp.tool(
        name="get_issue",
        description="Get detailed information about a specific GitHub issue.",
    )
    def get_issue_tool(
        owner: str = Field(..., description="Repository owner name."),
        repo: str = Field(..., description="Repository name."),
        issue_number: int = Field(..., description="Issue number."),
    ) -> str:
        tlog = ToolLogger(logger, "get_issue")
        try:
            data = get_issue(owner, repo, issue_number)
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
                error=ToolError(code="INTERNAL_ERROR", message="Unexpected error while fetching issue.", details={"exception": str(exc)}),
            ).model_dump(mode="json"))

    @mcp.tool(
        name="get_issue_comments",
        description="Get all comments on a GitHub issue with pagination support.",
    )
    def get_issue_comments_tool(
        owner: str = Field(..., description="Repository owner name."),
        repo: str = Field(..., description="Repository name."),
        issue_number: int = Field(..., description="Issue number."),
        page: int = Field(1, description="Page number."),
        perPage: int = Field(30, description="Comments per page (1-100)."),
    ) -> str:
        tlog = ToolLogger(logger, "get_issue_comments")
        try:
            data = get_issue_comments(owner, repo, issue_number, page=page, per_page=perPage)
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
                error=ToolError(code="INTERNAL_ERROR", message="Unexpected error while fetching issue comments.", details={"exception": str(exc)}),
            ).model_dump(mode="json"))

    @mcp.tool(
        name="create_issue",
        description="Create a new GitHub issue in a repository.",
    )
    def create_issue_tool(
        owner: str = Field(..., description="Repository owner name."),
        repo: str = Field(..., description="Repository name."),
        title: str = Field(..., description="Issue title (required)."),
        body: str | None = Field(None, description="Issue description (optional)."),
        assignees: list[str] | None = Field(None, description="List of usernames to assign (optional)."),
        labels: list[str] | None = Field(None, description="List of label names (optional)."),
        milestone: int | None = Field(None, description="Milestone ID (optional)."),
    ) -> str:
        tlog = ToolLogger(logger, "create_issue")
        try:
            data = create_issue(owner, repo, title, body=body, assignees=assignees, labels=labels, milestone=milestone)
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
                error=ToolError(code="INTERNAL_ERROR", message="Unexpected error while creating issue.", details={"exception": str(exc)}),
            ).model_dump(mode="json"))

    @mcp.tool(
        name="add_issue_comment",
        description="Add a comment to a GitHub issue or pull request.",
    )
    def add_issue_comment_tool(
        owner: str = Field(..., description="Repository owner name."),
        repo: str = Field(..., description="Repository name."),
        issue_number: int = Field(..., description="Issue or pull request number."),
        body: str = Field(..., description="Comment text (required)."),
    ) -> str:
        tlog = ToolLogger(logger, "add_issue_comment")
        try:
            data = add_issue_comment(owner, repo, issue_number, body)
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
                error=ToolError(code="INTERNAL_ERROR", message="Unexpected error while adding comment.", details={"exception": str(exc)}),
            ).model_dump(mode="json"))

    @mcp.tool(
        name="update_issue",
        description="Update GitHub issue properties including title, body, state, assignees, and labels.",
    )
    def update_issue_tool(
        owner: str = Field(..., description="Repository owner name."),
        repo: str = Field(..., description="Repository name."),
        issue_number: int = Field(..., description="Issue number to update."),
        title: str | None = Field(None, description="New issue title (optional)."),
        body: str | None = Field(None, description="New issue description (optional)."),
        state: str | None = Field(None, description="New state: open or closed (optional)."),
        state_reason: str | None = Field(None, description="Reason when closing: completed, not_planned (optional)."),
        assignees: list[str] | None = Field(None, description="New list of assignees (optional)."),
        labels: list[str] | None = Field(None, description="New list of labels (optional)."),
        milestone: int | None = Field(None, description="Milestone ID (optional)."),
    ) -> str:
        tlog = ToolLogger(logger, "update_issue")
        try:
            data = update_issue(owner, repo, issue_number, title=title, body=body, state=state, state_reason=state_reason, assignees=assignees, labels=labels, milestone=milestone)
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
                error=ToolError(code="INTERNAL_ERROR", message="Unexpected error while updating issue.", details={"exception": str(exc)}),
            ).model_dump(mode="json"))

    @mcp.tool(
        name="list_org_repositories_by_contributor",
        description="Find all repositories in an organization where specific contributors have made contributions.",
    )
    def list_org_repositories_by_contributor_tool(
        org: str = Field(..., description="Organization name"),
        contributor_usernames: str = Field(..., description="GitHub username(s) to filter by. Comma-separated for multiple."),
        repo_type: str = Field("all", description="Filter by type: all, public, or private."),
    ) -> str:
        tlog = ToolLogger(logger, "list_org_repositories_by_contributor")
        try:
            usernames_list = [u.strip() for u in contributor_usernames.split(",") if u.strip()]
            data = list_org_repositories_by_contributor(org, usernames_list, repo_type=repo_type)
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
                error=ToolError(code="INTERNAL_ERROR", message="Unexpected error.", details={"exception": str(exc)}),
            ).model_dump(mode="json"))

    @mcp.tool(
        name="sub_issue_write",
        description="Manage sub-issues for a parent issue (add, remove, reprioritize).",
    )
    def sub_issue_write_tool(
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        issue_number: int = Field(..., description="Parent issue number"),
        method: str = Field(..., description="Operation: add, remove, or reprioritize"),
        sub_issue_id: int = Field(..., description="ID of the sub-issue"),
        replace_parent: bool = Field(False, description="Replace current parent when adding"),
        after_id: int | None = Field(None, description="Sub-issue ID to position after"),
        before_id: int | None = Field(None, description="Sub-issue ID to position before"),
    ) -> str:
        tlog = ToolLogger(logger, "sub_issue_write")
        try:
            data = sub_issue_write(owner, repo, issue_number, method=method, sub_issue_id=sub_issue_id, replace_parent=replace_parent, after_id=after_id, before_id=before_id)
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
                error=ToolError(code="INTERNAL_ERROR", message="Unexpected error.", details={"exception": str(exc)}),
            ).model_dump(mode="json"))

    @mcp.tool(
        name="assign_copilot_to_issue",
        description="Assign GitHub Copilot to work on an issue.",
    )
    def assign_copilot_to_issue_tool(
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        issue_number: int = Field(..., description="Issue number"),
        base_ref: str | None = Field(None, description="Git reference to start from (optional)."),
        custom_instructions: str | None = Field(None, description="Additional context for Copilot (optional)."),
    ) -> str:
        tlog = ToolLogger(logger, "assign_copilot_to_issue")
        try:
            data = assign_copilot_to_issue(owner, repo, issue_number, base_ref=base_ref, custom_instructions=custom_instructions)
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
                error=ToolError(code="INTERNAL_ERROR", message="Unexpected error.", details={"exception": str(exc)}),
            ).model_dump(mode="json"))
