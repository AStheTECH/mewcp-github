import json
import logging
from fastmcp import FastMCP
from pydantic import Field

from ..schemas import ToolError, ToolResult
from ..logging_utils import ToolLogger
from ._helpers import _err, _handle_request_exc, _upstream_err
from ..service import (
    pull_request_read,
    list_pull_requests,
    create_pull_request,
    update_pull_request,
    merge_pull_request,
    update_pull_request_branch,
    pull_request_review_write,
    add_reply_to_pull_request_comment,
    request_copilot_review,
    GitHubServiceError,
)

logger = logging.getLogger("github-mcp-server")


def register_pr_tools(mcp: FastMCP) -> None:

    @mcp.tool(
        name="pull_request_read",
        description="Get details for a pull request with flexible method options (get, get_files, get_status, get_comments, get_review_comments).",
    )
    def pr_read(
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        pull_number: int = Field(..., description="Pull request number"),
        method: str = Field("get", description="Which PR data to retrieve: get, get_files, get_status, get_comments, get_review_comments"),
        page: int = Field(1, description="Page number"),
        per_page: int = Field(30, description="Results per page"),
    ) -> str:
        tlog = ToolLogger(logger, "pull_request_read")
        try:
            result = pull_request_read(owner=owner, repo=repo, pull_number=pull_number, method=method, page=page, per_page=per_page)
            tlog.success()
            return json.dumps(ToolResult(success=True, statusCode=200, data=result).model_dump(mode="json"))
        except GitHubServiceError as exc:
            tlog.failure(exc.code, exc.message)
            return json.dumps(ToolResult(success=False, statusCode=exc.http_status or 400, error=ToolError(code=exc.code, message=exc.message, details=exc.details)).model_dump(mode="json"))
        except Exception as exc:
            tlog.failure("INTERNAL_ERROR", str(exc))
            return json.dumps(ToolResult(success=False, statusCode=500, error=ToolError(code="INTERNAL_ERROR", message="Unexpected error.", details={"exception": str(exc)})).model_dump(mode="json"))

    @mcp.tool(
        name="list_pull_requests",
        description="List pull requests in a GitHub repository with filtering and sorting options.",
    )
    def list_prs(
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        state: str = Field("open", description="Filter by state: open, closed, or all"),
        sort: str = Field("created", description="Sort by: created, updated, popularity, or long-running"),
        direction: str = Field("desc", description="Sort direction: asc or desc"),
        base: str | None = Field(None, description="Filter by base branch"),
        head: str | None = Field(None, description="Filter by head branch (user:branch format)"),
        page: int = Field(1, description="Page number"),
        per_page: int = Field(30, description="Results per page"),
    ) -> str:
        tlog = ToolLogger(logger, "list_pull_requests")
        try:
            result = list_pull_requests(owner=owner, repo=repo, state=state, sort=sort, direction=direction, base=base, head=head, page=page, per_page=per_page)
            tlog.success()
            return json.dumps(ToolResult(success=True, statusCode=200, data=result).model_dump(mode="json"))
        except GitHubServiceError as exc:
            tlog.failure(exc.code, exc.message)
            return json.dumps(ToolResult(success=False, statusCode=exc.http_status or 400, error=ToolError(code=exc.code, message=exc.message, details=exc.details)).model_dump(mode="json"))
        except Exception as exc:
            tlog.failure("INTERNAL_ERROR", str(exc))
            return json.dumps(ToolResult(success=False, statusCode=500, error=ToolError(code="INTERNAL_ERROR", message="Unexpected error.", details={"exception": str(exc)})).model_dump(mode="json"))

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
        body: str | None = Field(None, description="PR description (optional)"),
        draft: bool = Field(False, description="Create as draft PR"),
        maintainer_can_modify: bool = Field(True, description="Allow maintainer edits"),
    ) -> str:
        tlog = ToolLogger(logger, "create_pull_request")
        try:
            result = create_pull_request(owner=owner, repo=repo, title=title, head=head, base=base, body=body, draft=draft, maintainer_can_modify=maintainer_can_modify)
            tlog.success()
            return json.dumps(ToolResult(success=True, statusCode=200, data=result).model_dump(mode="json"))
        except GitHubServiceError as exc:
            tlog.failure(exc.code, exc.message)
            return json.dumps(ToolResult(success=False, statusCode=exc.http_status or 400, error=ToolError(code=exc.code, message=exc.message, details=exc.details)).model_dump(mode="json"))
        except Exception as exc:
            tlog.failure("INTERNAL_ERROR", str(exc))
            return json.dumps(ToolResult(success=False, statusCode=500, error=ToolError(code="INTERNAL_ERROR", message="Unexpected error.", details={"exception": str(exc)})).model_dump(mode="json"))

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
        maintainer_can_modify: bool | None = Field(None, description="Allow maintainer edits (optional)"),
        reviewers: list[str] | None = Field(None, description="Request reviews from users (optional)"),
    ) -> str:
        tlog = ToolLogger(logger, "update_pull_request")
        try:
            result = update_pull_request(owner=owner, repo=repo, pull_number=pull_number, title=title, body=body, state=state, base=base, draft=draft, maintainer_can_modify=maintainer_can_modify, reviewers=reviewers)
            tlog.success()
            return json.dumps(ToolResult(success=True, statusCode=200, data=result).model_dump(mode="json"))
        except GitHubServiceError as exc:
            tlog.failure(exc.code, exc.message)
            return json.dumps(ToolResult(success=False, statusCode=exc.http_status or 400, error=ToolError(code=exc.code, message=exc.message, details=exc.details)).model_dump(mode="json"))
        except Exception as exc:
            tlog.failure("INTERNAL_ERROR", str(exc))
            return json.dumps(ToolResult(success=False, statusCode=500, error=ToolError(code="INTERNAL_ERROR", message="Unexpected error.", details={"exception": str(exc)})).model_dump(mode="json"))

    @mcp.tool(
        name="merge_pull_request",
        description="Merge a pull request in a GitHub repository.",
    )
    def merge_pr(
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        pull_number: int = Field(..., description="Pull request number"),
        merge_method: str = Field("merge", description="'merge', 'squash', or 'rebase'"),
        commit_title: str | None = Field(None, description="Custom commit title (optional)"),
        commit_message: str | None = Field(None, description="Commit message details (optional)"),
    ) -> str:
        tlog = ToolLogger(logger, "merge_pull_request")
        try:
            result = merge_pull_request(owner=owner, repo=repo, pull_number=pull_number, merge_method=merge_method, commit_title=commit_title, commit_message=commit_message)
            tlog.success()
            return json.dumps(ToolResult(success=True, statusCode=200, data=result).model_dump(mode="json"))
        except GitHubServiceError as exc:
            tlog.failure(exc.code, exc.message)
            return json.dumps(ToolResult(success=False, statusCode=exc.http_status or 400, error=ToolError(code=exc.code, message=exc.message, details=exc.details)).model_dump(mode="json"))
        except Exception as exc:
            tlog.failure("INTERNAL_ERROR", str(exc))
            return json.dumps(ToolResult(success=False, statusCode=500, error=ToolError(code="INTERNAL_ERROR", message="Unexpected error.", details={"exception": str(exc)})).model_dump(mode="json"))

    @mcp.tool(
        name="update_pull_request_branch",
        description="Update pull request branch with latest changes from base branch.",
    )
    def update_pr_branch(
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        pull_number: int = Field(..., description="Pull request number"),
        expected_head_sha: str | None = Field(None, description="Expected HEAD SHA (optional)"),
    ) -> str:
        tlog = ToolLogger(logger, "update_pull_request_branch")
        try:
            result = update_pull_request_branch(owner=owner, repo=repo, pull_number=pull_number, expected_head_sha=expected_head_sha)
            tlog.success()
            return json.dumps(ToolResult(success=True, statusCode=200, data=result).model_dump(mode="json"))
        except GitHubServiceError as exc:
            tlog.failure(exc.code, exc.message)
            return json.dumps(ToolResult(success=False, statusCode=exc.http_status or 400, error=ToolError(code=exc.code, message=exc.message, details=exc.details)).model_dump(mode="json"))
        except Exception as exc:
            tlog.failure("INTERNAL_ERROR", str(exc))
            return json.dumps(ToolResult(success=False, statusCode=500, error=ToolError(code="INTERNAL_ERROR", message="Unexpected error.", details={"exception": str(exc)})).model_dump(mode="json"))

    @mcp.tool(
        name="pull_request_review_write",
        description="Write operations on PR reviews (create, submit, delete, resolve/unresolve threads).",
    )
    def pr_review_write(
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        pull_number: int = Field(..., description="Pull request number"),
        method: str = Field(..., description="create, submit_pending, delete_pending, resolve_thread, or unresolve_thread"),
        commit_id: str | None = Field(None, description="Commit SHA (required for create)"),
        body: str | None = Field(None, description="Review comment text (optional)"),
        event: str | None = Field(None, description="APPROVE, REQUEST_CHANGES, or COMMENT"),
        thread_id: str | None = Field(None, description="Thread ID for thread operations"),
    ) -> str:
        tlog = ToolLogger(logger, "pull_request_review_write")
        try:
            result = pull_request_review_write(owner=owner, repo=repo, pull_number=pull_number, method=method, commit_id=commit_id, body=body, event=event, thread_id=thread_id)
            tlog.success()
            return json.dumps(ToolResult(success=True, statusCode=200, data=result).model_dump(mode="json"))
        except GitHubServiceError as exc:
            tlog.failure(exc.code, exc.message)
            return json.dumps(ToolResult(success=False, statusCode=exc.http_status or 400, error=ToolError(code=exc.code, message=exc.message, details=exc.details)).model_dump(mode="json"))
        except Exception as exc:
            tlog.failure("INTERNAL_ERROR", str(exc))
            return json.dumps(ToolResult(success=False, statusCode=500, error=ToolError(code="INTERNAL_ERROR", message="Unexpected error.", details={"exception": str(exc)})).model_dump(mode="json"))

    @mcp.tool(
        name="add_reply_to_pull_request_comment",
        description="Add a reply to an existing PR comment.",
    )
    def add_reply_to_pr_comment(
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        pull_number: int = Field(..., description="Pull request number"),
        comment_id: int = Field(..., description="ID of the comment to reply to"),
        body: str = Field(..., description="Reply text"),
    ) -> str:
        tlog = ToolLogger(logger, "add_reply_to_pull_request_comment")
        try:
            result = add_reply_to_pull_request_comment(owner=owner, repo=repo, pull_number=pull_number, comment_id=comment_id, body=body)
            tlog.success()
            return json.dumps(ToolResult(success=True, statusCode=200, data=result).model_dump(mode="json"))
        except GitHubServiceError as exc:
            tlog.failure(exc.code, exc.message)
            return json.dumps(ToolResult(success=False, statusCode=exc.http_status or 400, error=ToolError(code=exc.code, message=exc.message, details=exc.details)).model_dump(mode="json"))
        except Exception as exc:
            tlog.failure("INTERNAL_ERROR", str(exc))
            return json.dumps(ToolResult(success=False, statusCode=500, error=ToolError(code="INTERNAL_ERROR", message="Unexpected error.", details={"exception": str(exc)})).model_dump(mode="json"))

    @mcp.tool(
        name="request_copilot_review",
        description="Request a code review from GitHub Copilot on a pull request.",
    )
    def request_copilot_review_tool(
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        pull_number: int = Field(..., description="Pull request number"),
    ) -> str:
        tlog = ToolLogger(logger, "request_copilot_review")
        try:
            result = request_copilot_review(owner=owner, repo=repo, pull_number=pull_number)
            tlog.success()
            return json.dumps(ToolResult(success=True, statusCode=200, data=result).model_dump(mode="json"))
        except GitHubServiceError as exc:
            tlog.failure(exc.code, exc.message)
            return json.dumps(ToolResult(success=False, statusCode=exc.http_status or 400, error=ToolError(code=exc.code, message=exc.message, details=exc.details)).model_dump(mode="json"))
        except Exception as exc:
            tlog.failure("INTERNAL_ERROR", str(exc))
            return json.dumps(ToolResult(success=False, statusCode=500, error=ToolError(code="INTERNAL_ERROR", message="Unexpected error.", details={"exception": str(exc)})).model_dump(mode="json"))
