"""PR group: pull_request_read, list_pull_requests, create_pull_request,
update_pull_request, merge_pull_request, update_pull_request_branch,
pull_request_review_write, add_reply_to_pull_request_comment,
request_copilot_review"""

import logging

from fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from ..logging_utils import ToolLogger
from ..schemas import (
    AddReplyToPullRequestCommentData,
    AddReplyToPullRequestCommentResult,
    CreatePullRequestData,
    CreatePullRequestResult,
    ListPullRequestsData,
    ListPullRequestsResult,
    MergePullRequestData,
    MergePullRequestResult,
    PullRequestReadData,
    PullRequestReadResult,
    PullRequestReviewWriteData,
    PullRequestReviewWriteResult,
    RequestCopilotReviewData,
    RequestCopilotReviewResult,
    UpdatePullRequestBranchData,
    UpdatePullRequestBranchResult,
    UpdatePullRequestData,
    UpdatePullRequestResult,
    UpdatePullRequestUpdateData,
)
from ._helpers import _err, _handle_service_exc
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
)

logger = logging.getLogger("github-mcp-server")

_VALID_MERGE_METHODS = ("merge", "squash", "rebase")
_VALID_REVIEW_METHODS = (
    "create",
    "submit_pending",
    "delete_pending",
    "resolve_thread",
    "unresolve_thread",
)
_VALID_REVIEW_EVENTS = ("APPROVE", "REQUEST_CHANGES", "COMMENT")


def register_pr_tools(mcp: FastMCP) -> None:

    @mcp.tool(
        name="pull_request_read",
        description="Get details for a pull request with flexible method options (get, get_files, get_status, get_comments, get_review_comments).",
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True),
    )
    def pr_read(
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        pull_number: int = Field(..., description="Pull request number"),
        method: str = Field("get", description="Which PR data to retrieve: get, get_files, get_status, get_comments, get_review_comments"),
        page: int = Field(1, description="Page number"),
        per_page: int = Field(30, description="Results per page"),
    ) -> PullRequestReadResult:
        tlog = ToolLogger(logger, "pull_request_read")
        try:
            result = pull_request_read(owner=owner, repo=repo, pull_number=pull_number, method=method, page=page, per_page=per_page)
            tlog.success()
            return PullRequestReadResult(success=True, statusCode=200, data=PullRequestReadData(**result))
        except Exception as exc:
            return _handle_service_exc(PullRequestReadResult, tlog, exc)

    @mcp.tool(
        name="list_pull_requests",
        description="List pull requests in a GitHub repository with filtering and sorting options.",
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True),
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
    ) -> ListPullRequestsResult:
        tlog = ToolLogger(logger, "list_pull_requests")
        try:
            result = list_pull_requests(owner=owner, repo=repo, state=state, sort=sort, direction=direction, base=base, head=head, page=page, per_page=per_page)
            tlog.success()
            return ListPullRequestsResult(success=True, statusCode=200, data=ListPullRequestsData(**result))
        except Exception as exc:
            return _handle_service_exc(ListPullRequestsResult, tlog, exc)

    @mcp.tool(
        name="create_pull_request",
        description="Create a new pull request in a GitHub repository.",
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=True),
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
    ) -> CreatePullRequestResult:
        tlog = ToolLogger(logger, "create_pull_request")
        try:
            result = create_pull_request(owner=owner, repo=repo, title=title, head=head, base=base, body=body, draft=draft, maintainer_can_modify=maintainer_can_modify)
            tlog.success()
            return CreatePullRequestResult(success=True, statusCode=200, data=CreatePullRequestData(**result))
        except Exception as exc:
            return _handle_service_exc(CreatePullRequestResult, tlog, exc)

    @mcp.tool(
        name="update_pull_request",
        description=(
            "Updates a pull request's title, body, state, base branch, draft status, maintainer-edit permission, "
            "or requested reviewers. Only the fields you provide are changed — others keep their current value. "
            "NOTE: this overwrites the current field values — the original state is not stored after the call. "
            "The response includes both the before and after state so you have a full record of what changed."
        ),
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=True),
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
    ) -> UpdatePullRequestResult:
        tlog = ToolLogger(logger, "update_pull_request")

        if all(v is None for v in (title, body, state, base, draft, maintainer_can_modify, reviewers)):
            return _err(
                UpdatePullRequestResult,
                tlog,
                "VALIDATION_ERROR",
                "At least one of title, body, state, base, draft, maintainer_can_modify, or reviewers must be provided.",
                400,
            )

        try:
            before_dict = pull_request_read(owner=owner, repo=repo, pull_number=pull_number, method="get")
            before = PullRequestReadData(**before_dict)

            after_dict = update_pull_request(owner=owner, repo=repo, pull_number=pull_number, title=title, body=body, state=state, base=base, draft=draft, maintainer_can_modify=maintainer_can_modify, reviewers=reviewers)
            after = UpdatePullRequestData(**after_dict)

            tlog.success()
            return UpdatePullRequestResult(
                success=True,
                statusCode=200,
                data=UpdatePullRequestUpdateData(before=before, after=after),
            )
        except Exception as exc:
            return _handle_service_exc(UpdatePullRequestResult, tlog, exc)

    @mcp.tool(
        name="merge_pull_request",
        description=(
            "Merges a pull request using the given merge method (merge, squash, or rebase). "
            "This action is irreversible — once merged, the pull request cannot be un-merged; "
            "undoing it requires a new commit or pull request."
        ),
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=True),
    )
    def merge_pr(
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        pull_number: int = Field(..., description="Pull request number"),
        merge_method: str = Field("merge", description="'merge', 'squash', or 'rebase'"),
        commit_title: str | None = Field(None, description="Custom commit title (optional)"),
        commit_message: str | None = Field(None, description="Commit message details (optional)"),
    ) -> MergePullRequestResult:
        tlog = ToolLogger(logger, "merge_pull_request")

        if merge_method not in _VALID_MERGE_METHODS:
            return _err(
                MergePullRequestResult,
                tlog,
                "VALIDATION_ERROR",
                f"merge_method must be one of {', '.join(_VALID_MERGE_METHODS)}.",
                400,
            )

        try:
            result = merge_pull_request(owner=owner, repo=repo, pull_number=pull_number, merge_method=merge_method, commit_title=commit_title, commit_message=commit_message)
            tlog.success()
            return MergePullRequestResult(success=True, statusCode=200, data=MergePullRequestData(**result))
        except Exception as exc:
            return _handle_service_exc(MergePullRequestResult, tlog, exc)

    @mcp.tool(
        name="update_pull_request_branch",
        description="Update pull request branch with latest changes from base branch.",
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=True),
    )
    def update_pr_branch(
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        pull_number: int = Field(..., description="Pull request number"),
        expected_head_sha: str | None = Field(None, description="Expected HEAD SHA (optional)"),
    ) -> UpdatePullRequestBranchResult:
        tlog = ToolLogger(logger, "update_pull_request_branch")
        try:
            result = update_pull_request_branch(owner=owner, repo=repo, pull_number=pull_number, expected_head_sha=expected_head_sha)
            tlog.success()
            return UpdatePullRequestBranchResult(success=True, statusCode=200, data=UpdatePullRequestBranchData(**result))
        except Exception as exc:
            return _handle_service_exc(UpdatePullRequestBranchResult, tlog, exc)

    @mcp.tool(
        name="pull_request_review_write",
        description=(
            "Write operations on PR reviews: create a review, submit a pending review, delete a pending review, "
            "or resolve/unresolve a review thread. Select the operation via `method`. "
            "NOTE: `delete_pending` permanently discards an unsubmitted draft review and any draft comments on it — "
            "this cannot be undone."
        ),
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=True),
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
    ) -> PullRequestReviewWriteResult:
        tlog = ToolLogger(logger, "pull_request_review_write")

        if method not in _VALID_REVIEW_METHODS:
            return _err(
                PullRequestReviewWriteResult,
                tlog,
                "VALIDATION_ERROR",
                f"method must be one of {', '.join(_VALID_REVIEW_METHODS)}.",
                400,
            )
        if method == "create" and not commit_id:
            return _err(
                PullRequestReviewWriteResult,
                tlog,
                "VALIDATION_ERROR",
                "commit_id is required when method='create'.",
                400,
            )
        if method == "submit_pending":
            if not event:
                return _err(
                    PullRequestReviewWriteResult,
                    tlog,
                    "VALIDATION_ERROR",
                    "event is required when method='submit_pending'.",
                    400,
                )
            if event not in _VALID_REVIEW_EVENTS:
                return _err(
                    PullRequestReviewWriteResult,
                    tlog,
                    "VALIDATION_ERROR",
                    f"event must be one of {', '.join(_VALID_REVIEW_EVENTS)}.",
                    400,
                )
        if method in ("resolve_thread", "unresolve_thread") and not thread_id:
            return _err(
                PullRequestReviewWriteResult,
                tlog,
                "VALIDATION_ERROR",
                f"thread_id is required when method='{method}'.",
                400,
            )

        try:
            result = pull_request_review_write(owner=owner, repo=repo, pull_number=pull_number, method=method, commit_id=commit_id, body=body, event=event, thread_id=thread_id)
            tlog.success()
            return PullRequestReviewWriteResult(success=True, statusCode=200, data=PullRequestReviewWriteData(**result))
        except Exception as exc:
            return _handle_service_exc(PullRequestReviewWriteResult, tlog, exc)

    @mcp.tool(
        name="add_reply_to_pull_request_comment",
        description="Add a reply to an existing PR comment.",
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=True),
    )
    def add_reply_to_pr_comment(
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        pull_number: int = Field(..., description="Pull request number"),
        comment_id: int = Field(..., description="ID of the comment to reply to"),
        body: str = Field(..., description="Reply text"),
    ) -> AddReplyToPullRequestCommentResult:
        tlog = ToolLogger(logger, "add_reply_to_pull_request_comment")
        try:
            result = add_reply_to_pull_request_comment(owner=owner, repo=repo, pull_number=pull_number, comment_id=comment_id, body=body)
            tlog.success()
            return AddReplyToPullRequestCommentResult(success=True, statusCode=200, data=AddReplyToPullRequestCommentData(**result))
        except Exception as exc:
            return _handle_service_exc(AddReplyToPullRequestCommentResult, tlog, exc)

    @mcp.tool(
        name="request_copilot_review",
        description="Request a code review from GitHub Copilot on a pull request.",
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=True),
    )
    def request_copilot_review_tool(
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        pull_number: int = Field(..., description="Pull request number"),
    ) -> RequestCopilotReviewResult:
        tlog = ToolLogger(logger, "request_copilot_review")
        try:
            result = request_copilot_review(owner=owner, repo=repo, pull_number=pull_number)
            tlog.success()
            return RequestCopilotReviewResult(success=True, statusCode=200, data=RequestCopilotReviewData(**result))
        except Exception as exc:
            return _handle_service_exc(RequestCopilotReviewResult, tlog, exc)
