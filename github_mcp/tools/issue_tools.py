import logging
from fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from ..schemas import (
    ListIssuesData,
    ListIssuesResult,
    GetIssueData,
    GetIssueResult,
    GetIssueCommentsData,
    GetIssueCommentsResult,
    CreateIssueData,
    CreateIssueResult,
    AddIssueCommentData,
    AddIssueCommentResult,
    UpdateIssueData,
    UpdateIssueUpdateData,
    UpdateIssueResult,
    ListOrgRepositoriesByContributorData,
    ListOrgRepositoriesByContributorResult,
    SubIssueWriteData,
    SubIssueWriteResult,
    AssignCopilotToIssueData,
    AssignCopilotToIssueResult,
)
from ..logging_utils import ToolLogger
from ._helpers import _err, _handle_service_exc
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
)

logger = logging.getLogger("github-mcp-server")


def register_issue_tools(mcp: FastMCP) -> None:

    @mcp.tool(
        name="list_issues",
        description="List issues in a GitHub repository.",
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True),
    )
    def list_issues_tool(
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        state: str = Field("open", description="Filter by state: open, closed, all"),
        labels: str | None = Field(None, description="Comma-separated label names to filter by"),
        page: int = Field(1, description="Page number"),
        perPage: int = Field(30, description="Items per page"),
    ) -> ListIssuesResult:
        tlog = ToolLogger(logger, "list_issues")
        try:
            data = list_issues(owner, repo, state=state, labels=labels, page=page, per_page=perPage)
            tlog.success()
            return ListIssuesResult(success=True, statusCode=200, data=ListIssuesData(**data))
        except Exception as exc:
            return _handle_service_exc(ListIssuesResult, tlog, exc)

    @mcp.tool(
        name="get_issue",
        description="Get detailed information about a specific GitHub issue.",
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True),
    )
    def get_issue_tool(
        owner: str = Field(..., description="Repository owner name."),
        repo: str = Field(..., description="Repository name."),
        issue_number: int = Field(..., description="Issue number."),
    ) -> GetIssueResult:
        tlog = ToolLogger(logger, "get_issue")
        try:
            data = get_issue(owner, repo, issue_number)
            tlog.success()
            return GetIssueResult(success=True, statusCode=200, data=GetIssueData(**data))
        except Exception as exc:
            return _handle_service_exc(GetIssueResult, tlog, exc)

    @mcp.tool(
        name="get_issue_comments",
        description="Get all comments on a GitHub issue with pagination support.",
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True),
    )
    def get_issue_comments_tool(
        owner: str = Field(..., description="Repository owner name."),
        repo: str = Field(..., description="Repository name."),
        issue_number: int = Field(..., description="Issue number."),
        page: int = Field(1, description="Page number."),
        perPage: int = Field(30, description="Comments per page (1-100)."),
    ) -> GetIssueCommentsResult:
        tlog = ToolLogger(logger, "get_issue_comments")
        try:
            data = get_issue_comments(owner, repo, issue_number, page=page, per_page=perPage)
            tlog.success()
            return GetIssueCommentsResult(success=True, statusCode=200, data=GetIssueCommentsData(**data))
        except Exception as exc:
            return _handle_service_exc(GetIssueCommentsResult, tlog, exc)

    @mcp.tool(
        name="create_issue",
        description="Create a new GitHub issue in a repository.",
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=True),
    )
    def create_issue_tool(
        owner: str = Field(..., description="Repository owner name."),
        repo: str = Field(..., description="Repository name."),
        title: str = Field(..., description="Issue title (required)."),
        body: str | None = Field(None, description="Issue description (optional)."),
        assignees: list[str] | None = Field(None, description="List of usernames to assign (optional)."),
        labels: list[str] | None = Field(None, description="List of label names (optional)."),
        milestone: int | None = Field(None, description="Milestone ID (optional)."),
    ) -> CreateIssueResult:
        tlog = ToolLogger(logger, "create_issue")
        try:
            data = create_issue(owner, repo, title, body=body, assignees=assignees, labels=labels, milestone=milestone)
            tlog.success()
            return CreateIssueResult(success=True, statusCode=200, data=CreateIssueData(**data))
        except Exception as exc:
            return _handle_service_exc(CreateIssueResult, tlog, exc)

    @mcp.tool(
        name="add_issue_comment",
        description="Add a comment to a GitHub issue or pull request.",
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=True),
    )
    def add_issue_comment_tool(
        owner: str = Field(..., description="Repository owner name."),
        repo: str = Field(..., description="Repository name."),
        issue_number: int = Field(..., description="Issue or pull request number."),
        body: str = Field(..., description="Comment text (required)."),
    ) -> AddIssueCommentResult:
        tlog = ToolLogger(logger, "add_issue_comment")
        try:
            data = add_issue_comment(owner, repo, issue_number, body)
            tlog.success()
            return AddIssueCommentResult(success=True, statusCode=200, data=AddIssueCommentData(**data))
        except Exception as exc:
            return _handle_service_exc(AddIssueCommentResult, tlog, exc)

    @mcp.tool(
        name="update_issue",
        description=(
            "Updates a GitHub issue's title, body, state, assignees, labels, or milestone. Only the "
            "fields you provide are changed — others keep their current value. NOTE: this overwrites "
            "the current field values — the original state is not stored after the call. The response "
            "includes both the before and after state so you have a full record of what changed."
        ),
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=True),
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
    ) -> UpdateIssueResult:
        tlog = ToolLogger(logger, "update_issue")

        if (
            title is None
            and body is None
            and state is None
            and state_reason is None
            and assignees is None
            and labels is None
            and milestone is None
        ):
            return _err(
                UpdateIssueResult,
                tlog,
                "VALIDATION_ERROR",
                "At least one field must be provided to update",
                400,
            )

        try:
            before = get_issue(owner, repo, issue_number)
            after = update_issue(
                owner, repo, issue_number,
                title=title, body=body, state=state, state_reason=state_reason,
                assignees=assignees, labels=labels, milestone=milestone,
            )
            tlog.success()
            return UpdateIssueResult(
                success=True,
                statusCode=200,
                data=UpdateIssueUpdateData(
                    before=GetIssueData(**before),
                    after=UpdateIssueData(**after),
                ),
            )
        except Exception as exc:
            return _handle_service_exc(UpdateIssueResult, tlog, exc)

    @mcp.tool(
        name="list_org_repositories_by_contributor",
        description="Find all repositories in an organization where specific contributors have made contributions.",
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True),
    )
    def list_org_repositories_by_contributor_tool(
        org: str = Field(..., description="Organization name"),
        contributor_usernames: str = Field(..., description="GitHub username(s) to filter by. Comma-separated for multiple."),
        repo_type: str = Field("all", description="Filter by type: all, public, or private."),
    ) -> ListOrgRepositoriesByContributorResult:
        tlog = ToolLogger(logger, "list_org_repositories_by_contributor")

        usernames_list = [u.strip() for u in contributor_usernames.split(",") if u.strip()]
        if not usernames_list:
            return _err(
                ListOrgRepositoriesByContributorResult,
                tlog,
                "VALIDATION_ERROR",
                "contributor_usernames must contain at least one non-empty username",
                400,
            )

        try:
            data = list_org_repositories_by_contributor(org, usernames_list, repo_type=repo_type)
            tlog.success()
            return ListOrgRepositoriesByContributorResult(
                success=True, statusCode=200, data=ListOrgRepositoriesByContributorData(**data)
            )
        except Exception as exc:
            return _handle_service_exc(ListOrgRepositoriesByContributorResult, tlog, exc)

    @mcp.tool(
        name="sub_issue_write",
        description="Manage sub-issues for a parent issue (add, remove, reprioritize).",
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=True),
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
    ) -> SubIssueWriteResult:
        tlog = ToolLogger(logger, "sub_issue_write")

        if method not in ("add", "remove", "reprioritize"):
            return _err(
                SubIssueWriteResult,
                tlog,
                "VALIDATION_ERROR",
                "method must be 'add', 'remove', or 'reprioritize'",
                400,
            )
        if method == "reprioritize" and not (after_id or before_id):
            return _err(
                SubIssueWriteResult,
                tlog,
                "VALIDATION_ERROR",
                "reprioritize method requires either after_id or before_id",
                400,
            )

        try:
            data = sub_issue_write(
                owner, repo, issue_number, method=method, sub_issue_id=sub_issue_id,
                replace_parent=replace_parent, after_id=after_id, before_id=before_id,
            )
            tlog.success()
            return SubIssueWriteResult(success=True, statusCode=200, data=SubIssueWriteData(**data))
        except Exception as exc:
            return _handle_service_exc(SubIssueWriteResult, tlog, exc)

    @mcp.tool(
        name="assign_copilot_to_issue",
        description="Assign GitHub Copilot to work on an issue.",
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=True),
    )
    def assign_copilot_to_issue_tool(
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        issue_number: int = Field(..., description="Issue number"),
        base_ref: str | None = Field(None, description="Git reference to start from (optional)."),
        custom_instructions: str | None = Field(None, description="Additional context for Copilot (optional)."),
    ) -> AssignCopilotToIssueResult:
        tlog = ToolLogger(logger, "assign_copilot_to_issue")
        try:
            data = assign_copilot_to_issue(owner, repo, issue_number, base_ref=base_ref, custom_instructions=custom_instructions)
            tlog.success()
            return AssignCopilotToIssueResult(success=True, statusCode=200, data=AssignCopilotToIssueData(**data))
        except Exception as exc:
            return _handle_service_exc(AssignCopilotToIssueResult, tlog, exc)
