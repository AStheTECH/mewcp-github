import logging
from fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from ..schemas import (
    ListBranchesData,
    ListBranchesResult,
    ListCommitsData,
    ListCommitsResult,
    GetCommitData,
    GetCommitResult,
    GetFileContentsData,
    GetFileContentsResult,
    ListTagsData,
    ListTagsResult,
    GetTagData,
    GetTagResult,
    GetLatestReleaseData,
    GetLatestReleaseResult,
    ListReleasesData,
    ListReleasesResult,
    GetReleaseByTagData,
    GetReleaseByTagResult,
    GetLabelData,
    GetLabelResult,
    GetMeData,
    GetMeResult,
    GetBranchProtectionData,
    GetBranchProtectionResult,
    SetBranchProtectionData,
    SetBranchProtectionResult,
    DeleteBranchProtectionData,
    DeleteBranchProtectionResult,
    GetPullRequestReviewProtectionData,
    GetPullRequestReviewProtectionResult,
    UpdatePullRequestReviewProtectionUpdateData,
    UpdatePullRequestReviewProtectionResult,
    DeletePullRequestReviewProtectionData,
    DeletePullRequestReviewProtectionResult,
    ListRepositoryRulesetsData,
    ListRepositoryRulesetsResult,
    GetRepositoryRulesetData,
    GetRepositoryRulesetResult,
    CreateRepositoryRulesetData,
    CreateRepositoryRulesetResult,
    UpdateRepositoryRulesetData,
    UpdateRepositoryRulesetUpdateData,
    UpdateRepositoryRulesetResult,
    DeleteRepositoryRulesetData,
    DeleteRepositoryRulesetResult,
)
from ..logging_utils import ToolLogger
from ._helpers import _err, _handle_service_exc
from ..service import (
    list_branches,
    list_commits,
    get_commit,
    get_file_contents,
    list_tags,
    get_tag,
    get_latest_release,
    list_releases,
    get_release_by_tag,
    get_label,
    get_me,
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


def register_misc_tools(mcp: FastMCP) -> None:

    @mcp.tool(
        name="list_branches",
        description="List branches in a GitHub repository.",
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True),
    )
    def list_branches_tool(
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        page: int = Field(1, description="Page number"),
        perPage: int = Field(30, description="Items per page"),
    ) -> ListBranchesResult:
        tlog = ToolLogger(logger, "list_branches")
        try:
            data = list_branches(owner, repo, page=page, per_page=perPage)
            tlog.success()
            return ListBranchesResult(success=True, statusCode=200, data=ListBranchesData(branches=data))
        except Exception as exc:
            return _handle_service_exc(ListBranchesResult, tlog, exc)

    @mcp.tool(
        name="list_commits",
        description="List commits in a GitHub repository.",
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True),
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
    ) -> ListCommitsResult:
        tlog = ToolLogger(logger, "list_commits")
        try:
            data = list_commits(owner, repo, sha=sha, path=path, author=author, since=since, until=until, page=page, per_page=perPage)
            tlog.success()
            return ListCommitsResult(success=True, statusCode=200, data=ListCommitsData(commits=data))
        except Exception as exc:
            return _handle_service_exc(ListCommitsResult, tlog, exc)

    @mcp.tool(
        name="get_commit",
        description="Get details of a specific commit.",
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True),
    )
    def get_commit_tool(
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        sha: str = Field(..., description="Commit SHA"),
        include_diff: bool = Field(True, description="Include file changes in diff"),
    ) -> GetCommitResult:
        tlog = ToolLogger(logger, "get_commit")
        try:
            data = get_commit(owner, repo, sha, include_diff=include_diff)
            tlog.success()
            return GetCommitResult(success=True, statusCode=200, data=GetCommitData(**data))
        except Exception as exc:
            return _handle_service_exc(GetCommitResult, tlog, exc)

    @mcp.tool(
        name="get_file_contents",
        description="Get file or directory contents from a GitHub repository.",
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True),
    )
    def get_file_contents_tool(
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        path: str = Field("/", description="File or directory path"),
        ref: str | None = Field(None, description="Branch, tag, or commit SHA"),
    ) -> GetFileContentsResult:
        tlog = ToolLogger(logger, "get_file_contents")
        try:
            data = get_file_contents(owner, repo, path=path, ref=ref)
            tlog.success()
            return GetFileContentsResult(success=True, statusCode=200, data=GetFileContentsData(**data))
        except Exception as exc:
            return _handle_service_exc(GetFileContentsResult, tlog, exc)

    @mcp.tool(
        name="list_tags",
        description="List all git tags in a repository with pagination support.",
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True),
    )
    def list_tags_tool(
        owner: str = Field(..., description="Repository owner name."),
        repo: str = Field(..., description="Repository name."),
        page: int = Field(1, description="Page number."),
        perPage: int = Field(30, description="Number of tags per page (1-100)."),
    ) -> ListTagsResult:
        tlog = ToolLogger(logger, "list_tags")
        try:
            data = list_tags(owner, repo, page=page, per_page=perPage)
            tlog.success()
            return ListTagsResult(success=True, statusCode=200, data=ListTagsData(**data))
        except Exception as exc:
            return _handle_service_exc(ListTagsResult, tlog, exc)

    @mcp.tool(
        name="get_tag",
        description="Get detailed information about a specific git tag.",
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True),
    )
    def get_tag_tool(
        owner: str = Field(..., description="Repository owner name."),
        repo: str = Field(..., description="Repository name."),
        tag: str = Field(..., description="Tag name to retrieve."),
    ) -> GetTagResult:
        tlog = ToolLogger(logger, "get_tag")
        try:
            data = get_tag(owner, repo, tag)
            tlog.success()
            return GetTagResult(success=True, statusCode=200, data=GetTagData(**data))
        except Exception as exc:
            return _handle_service_exc(GetTagResult, tlog, exc)

    @mcp.tool(
        name="get_latest_release",
        description="Get the latest release in a repository.",
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True),
    )
    def get_latest_release_tool(
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
    ) -> GetLatestReleaseResult:
        tlog = ToolLogger(logger, "get_latest_release")
        try:
            data = get_latest_release(owner, repo)
            tlog.success()
            return GetLatestReleaseResult(success=True, statusCode=200, data=GetLatestReleaseData(**data))
        except Exception as exc:
            return _handle_service_exc(GetLatestReleaseResult, tlog, exc)

    @mcp.tool(
        name="list_releases",
        description="List releases in a repository.",
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True),
    )
    def list_releases_tool(
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        page: int = Field(1, description="Page number"),
        per_page: int = Field(30, description="Results per page"),
    ) -> ListReleasesResult:
        tlog = ToolLogger(logger, "list_releases")
        try:
            data = list_releases(owner, repo, page=page, per_page=per_page)
            tlog.success()
            return ListReleasesResult(success=True, statusCode=200, data=ListReleasesData(**data))
        except Exception as exc:
            return _handle_service_exc(ListReleasesResult, tlog, exc)

    @mcp.tool(
        name="get_release_by_tag",
        description="Get a specific release by tag name.",
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True),
    )
    def get_release_by_tag_tool(
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        tag: str = Field(..., description="Tag name (e.g., 'v1.0.0')"),
    ) -> GetReleaseByTagResult:
        tlog = ToolLogger(logger, "get_release_by_tag")
        try:
            data = get_release_by_tag(owner, repo, tag)
            tlog.success()
            return GetReleaseByTagResult(success=True, statusCode=200, data=GetReleaseByTagData(**data))
        except Exception as exc:
            return _handle_service_exc(GetReleaseByTagResult, tlog, exc)

    @mcp.tool(
        name="get_label",
        description="Get a specific label from a repository.",
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True),
    )
    def get_label_tool(
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        name: str = Field(..., description="Label name"),
    ) -> GetLabelResult:
        tlog = ToolLogger(logger, "get_label")
        try:
            data = get_label(owner, repo, name)
            tlog.success()
            return GetLabelResult(success=True, statusCode=200, data=GetLabelData(**data))
        except Exception as exc:
            return _handle_service_exc(GetLabelResult, tlog, exc)

    @mcp.tool(
        name="get_me",
        description="Get details of the authenticated GitHub user.",
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True),
    )
    def get_me_tool() -> GetMeResult:
        tlog = ToolLogger(logger, "get_me")
        try:
            data = get_me()
            tlog.success()
            return GetMeResult(success=True, statusCode=200, data=GetMeData(**data))
        except Exception as exc:
            return _handle_service_exc(GetMeResult, tlog, exc)

    @mcp.tool(
        name="get_branch_protection",
        description="Get branch protection rules for a specific branch.",
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True),
    )
    def get_branch_protection_tool(
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        branch: str = Field(..., description="Branch name"),
    ) -> GetBranchProtectionResult:
        tlog = ToolLogger(logger, "get_branch_protection")
        try:
            data = get_branch_protection(owner, repo, branch)
            tlog.success()
            return GetBranchProtectionResult(success=True, statusCode=200, data=GetBranchProtectionData(**data))
        except Exception as exc:
            return _handle_service_exc(GetBranchProtectionResult, tlog, exc)

    @mcp.tool(
        name="set_branch_protection",
        description="Set (create or replace) branch protection rules for a branch.",
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=True),
    )
    def set_branch_protection_tool(
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        branch: str = Field(..., description="Branch name"),
        enforce_admins: bool = Field(..., description="Enforce for admins"),
        required_status_checks: dict | None = Field(None, description="Required status checks config"),
        required_pull_request_reviews: dict | None = Field(None, description="Required PR reviews config"),
        restrictions: dict | None = Field(None, description="User/team restrictions"),
        required_linear_history: bool = Field(False, description="Require linear history"),
        allow_force_pushes: bool | None = Field(None, description="Allow force pushes"),
        allow_deletions: bool = Field(False, description="Allow deletions"),
        block_creations: bool = Field(False, description="Block creations"),
        required_conversation_resolution: bool = Field(False, description="Require conversation resolution"),
        lock_branch: bool = Field(False, description="Lock branch"),
        allow_fork_syncing: bool = Field(False, description="Allow fork syncing"),
    ) -> SetBranchProtectionResult:
        tlog = ToolLogger(logger, "set_branch_protection")
        try:
            data = set_branch_protection(owner, repo, branch, enforce_admins=enforce_admins, required_status_checks=required_status_checks, required_pull_request_reviews=required_pull_request_reviews, restrictions=restrictions, required_linear_history=required_linear_history, allow_force_pushes=allow_force_pushes, allow_deletions=allow_deletions, block_creations=block_creations, required_conversation_resolution=required_conversation_resolution, lock_branch=lock_branch, allow_fork_syncing=allow_fork_syncing)
            tlog.success()
            return SetBranchProtectionResult(success=True, statusCode=200, data=SetBranchProtectionData(**data))
        except Exception as exc:
            return _handle_service_exc(SetBranchProtectionResult, tlog, exc)

    @mcp.tool(
        name="delete_branch_protection",
        description=(
            "DESTRUCTIVE — REQUIRES EXPLICIT USER CONFIRMATION BEFORE CALLING. "
            "Permanently deletes all branch protection rules for the given branch. "
            "This action is irreversible — the branch protection configuration (required status "
            "checks, required reviews, restrictions, and all other settings) cannot be recovered "
            "once deleted. NEVER call this tool autonomously or as part of an automated flow. "
            "You MUST stop, tell the user exactly what will be deleted and that it is permanent, "
            "and wait for their explicit written confirmation before proceeding."
        ),
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True, openWorldHint=True),
    )
    def delete_branch_protection_tool(
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        branch: str = Field(..., description="Branch name"),
    ) -> DeleteBranchProtectionResult:
        tlog = ToolLogger(logger, "delete_branch_protection")
        try:
            data = delete_branch_protection(owner, repo, branch)
            tlog.success()
            return DeleteBranchProtectionResult(success=True, statusCode=200, data=DeleteBranchProtectionData(**data))
        except Exception as exc:
            return _handle_service_exc(DeleteBranchProtectionResult, tlog, exc)

    @mcp.tool(
        name="get_pull_request_review_protection",
        description="Get PR review requirements for a protected branch.",
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True),
    )
    def get_pr_review_protection(
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        branch: str = Field(..., description="Branch name"),
    ) -> GetPullRequestReviewProtectionResult:
        tlog = ToolLogger(logger, "get_pull_request_review_protection")
        try:
            data = get_pull_request_review_protection(owner, repo, branch)
            tlog.success()
            return GetPullRequestReviewProtectionResult(success=True, statusCode=200, data=GetPullRequestReviewProtectionData(**data))
        except Exception as exc:
            return _handle_service_exc(GetPullRequestReviewProtectionResult, tlog, exc)

    @mcp.tool(
        name="update_pull_request_review_protection",
        description=(
            "Updates the pull request review requirements for a protected branch. Only the fields "
            "you provide are changed — others keep their current value. NOTE: this overwrites the "
            "current field values — the original state is not stored after the call. The response "
            "includes both the before and after state so you have a full record of what changed."
        ),
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=True),
    )
    def update_pr_review_protection(
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        branch: str = Field(..., description="Branch name"),
        dismiss_stale_reviews: bool | None = Field(None, description="Dismiss stale reviews"),
        require_code_owner_reviews: bool | None = Field(None, description="Require code owner reviews"),
        required_approving_review_count: int | None = Field(None, description="Required approving reviews"),
        require_last_push_approval: bool | None = Field(None, description="Require last push approval"),
        dismissal_restrictions: dict | None = Field(None, description="Dismissal restrictions"),
    ) -> UpdatePullRequestReviewProtectionResult:
        tlog = ToolLogger(logger, "update_pull_request_review_protection")

        if (
            dismiss_stale_reviews is None
            and require_code_owner_reviews is None
            and required_approving_review_count is None
            and require_last_push_approval is None
            and dismissal_restrictions is None
        ):
            return _err(
                UpdatePullRequestReviewProtectionResult,
                tlog,
                "VALIDATION_ERROR",
                "At least one field must be provided to update",
                400,
            )

        try:
            before = get_pull_request_review_protection(owner, repo, branch)
            after = update_pull_request_review_protection(owner, repo, branch, dismiss_stale_reviews=dismiss_stale_reviews, require_code_owner_reviews=require_code_owner_reviews, required_approving_review_count=required_approving_review_count, require_last_push_approval=require_last_push_approval, dismissal_restrictions=dismissal_restrictions)
            tlog.success()
            return UpdatePullRequestReviewProtectionResult(
                success=True,
                statusCode=200,
                data=UpdatePullRequestReviewProtectionUpdateData(
                    before=GetPullRequestReviewProtectionData(**before),
                    after=GetPullRequestReviewProtectionData(**after),
                ),
            )
        except Exception as exc:
            return _handle_service_exc(UpdatePullRequestReviewProtectionResult, tlog, exc)

    @mcp.tool(
        name="delete_pull_request_review_protection",
        description=(
            "DESTRUCTIVE — REQUIRES EXPLICIT USER CONFIRMATION BEFORE CALLING. "
            "Permanently removes the pull request review requirements from the given protected "
            "branch. This action is irreversible — the review requirement configuration (required "
            "approving review count, dismissal restrictions, code owner review requirement, and all "
            "other settings) cannot be recovered once deleted. NEVER call this tool autonomously or "
            "as part of an automated flow. You MUST stop, tell the user exactly what will be deleted "
            "and that it is permanent, and wait for their explicit written confirmation before "
            "proceeding."
        ),
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True, openWorldHint=True),
    )
    def delete_pr_review_protection(
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        branch: str = Field(..., description="Branch name"),
    ) -> DeletePullRequestReviewProtectionResult:
        tlog = ToolLogger(logger, "delete_pull_request_review_protection")
        try:
            data = delete_pull_request_review_protection(owner, repo, branch)
            tlog.success()
            return DeletePullRequestReviewProtectionResult(success=True, statusCode=200, data=DeletePullRequestReviewProtectionData(**data))
        except Exception as exc:
            return _handle_service_exc(DeletePullRequestReviewProtectionResult, tlog, exc)

    @mcp.tool(
        name="list_repository_rulesets",
        description="List all rulesets for a repository.",
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True),
    )
    def list_repository_rulesets_tool(
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        includes_parents: bool = Field(True, description="Include parent rulesets"),
        per_page: int = Field(30, description="Results per page"),
        page: int = Field(1, description="Page number"),
    ) -> ListRepositoryRulesetsResult:
        tlog = ToolLogger(logger, "list_repository_rulesets")
        try:
            data = list_repository_rulesets(owner, repo, includes_parents=includes_parents, per_page=per_page, page=page)
            tlog.success()
            return ListRepositoryRulesetsResult(success=True, statusCode=200, data=ListRepositoryRulesetsData(**data))
        except Exception as exc:
            return _handle_service_exc(ListRepositoryRulesetsResult, tlog, exc)

    @mcp.tool(
        name="get_repository_ruleset",
        description="Get a specific ruleset for a repository.",
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True),
    )
    def get_repository_ruleset_tool(
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        ruleset_id: int = Field(..., description="Ruleset ID"),
    ) -> GetRepositoryRulesetResult:
        tlog = ToolLogger(logger, "get_repository_ruleset")
        try:
            data = get_repository_ruleset(owner, repo, ruleset_id)
            tlog.success()
            return GetRepositoryRulesetResult(success=True, statusCode=200, data=GetRepositoryRulesetData(**data))
        except Exception as exc:
            return _handle_service_exc(GetRepositoryRulesetResult, tlog, exc)

    @mcp.tool(
        name="create_repository_ruleset",
        description="Create a new ruleset for a repository.",
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=True),
    )
    def create_repository_ruleset_tool(
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        name: str = Field(..., description="Ruleset name"),
        enforcement: str = Field(..., description="active, evaluate, or disabled"),
        target: str = Field("branch", description="Target: branch, tag, or push"),
        conditions: dict | None = Field(None, description="Ruleset conditions"),
        rules: list[dict] | None = Field(None, description="Rules list"),
        bypass_actors: list[dict] | None = Field(None, description="Bypass actors"),
    ) -> CreateRepositoryRulesetResult:
        tlog = ToolLogger(logger, "create_repository_ruleset")
        try:
            data = create_repository_ruleset(owner, repo, name, enforcement=enforcement, target=target, conditions=conditions, rules=rules, bypass_actors=bypass_actors)
            tlog.success()
            return CreateRepositoryRulesetResult(success=True, statusCode=200, data=CreateRepositoryRulesetData(**data))
        except Exception as exc:
            return _handle_service_exc(CreateRepositoryRulesetResult, tlog, exc)

    @mcp.tool(
        name="update_repository_ruleset",
        description=(
            "Updates an existing repository ruleset. Only the fields you provide are changed — "
            "others keep their current value. NOTE: this overwrites the current field values — the "
            "original state is not stored after the call. The response includes both the before and "
            "after state so you have a full record of what changed."
        ),
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=True),
    )
    def update_repository_ruleset_tool(
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        ruleset_id: int = Field(..., description="Ruleset ID"),
        name: str | None = Field(None, description="New ruleset name"),
        enforcement: str | None = Field(None, description="active, evaluate, or disabled"),
        target: str | None = Field(None, description="Updated target: branch, tag, or push"),
        conditions: dict | None = Field(None, description="Updated conditions"),
        rules: list[dict] | None = Field(None, description="Updated rules"),
        bypass_actors: list[dict] | None = Field(None, description="Updated bypass actors"),
    ) -> UpdateRepositoryRulesetResult:
        tlog = ToolLogger(logger, "update_repository_ruleset")

        if (
            name is None
            and enforcement is None
            and target is None
            and conditions is None
            and rules is None
            and bypass_actors is None
        ):
            return _err(
                UpdateRepositoryRulesetResult,
                tlog,
                "VALIDATION_ERROR",
                "At least one field must be provided to update",
                400,
            )

        try:
            before = get_repository_ruleset(owner, repo, ruleset_id)
            after = update_repository_ruleset(owner, repo, ruleset_id, name=name, enforcement=enforcement, target=target, conditions=conditions, rules=rules, bypass_actors=bypass_actors)
            tlog.success()
            return UpdateRepositoryRulesetResult(
                success=True,
                statusCode=200,
                data=UpdateRepositoryRulesetUpdateData(
                    before=GetRepositoryRulesetData(**before),
                    after=UpdateRepositoryRulesetData(**after),
                ),
            )
        except Exception as exc:
            return _handle_service_exc(UpdateRepositoryRulesetResult, tlog, exc)

    @mcp.tool(
        name="delete_repository_ruleset",
        description=(
            "DESTRUCTIVE — REQUIRES EXPLICIT USER CONFIRMATION BEFORE CALLING. "
            "Permanently deletes the specified ruleset from the repository. This action is "
            "irreversible — the ruleset configuration (conditions, rules, and bypass actors) cannot "
            "be recovered once deleted. NEVER call this tool autonomously or as part of an automated "
            "flow. You MUST stop, tell the user exactly what will be deleted and that it is "
            "permanent, and wait for their explicit written confirmation before proceeding."
        ),
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True, openWorldHint=True),
    )
    def delete_repository_ruleset_tool(
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        ruleset_id: int = Field(..., description="Ruleset ID"),
    ) -> DeleteRepositoryRulesetResult:
        tlog = ToolLogger(logger, "delete_repository_ruleset")
        try:
            data = delete_repository_ruleset(owner, repo, ruleset_id)
            tlog.success()
            return DeleteRepositoryRulesetResult(success=True, statusCode=200, data=DeleteRepositoryRulesetData(**data))
        except Exception as exc:
            return _handle_service_exc(DeleteRepositoryRulesetResult, tlog, exc)
