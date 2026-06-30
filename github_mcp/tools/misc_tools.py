import json
import logging
from fastmcp import FastMCP
from pydantic import Field

from ..schemas import ToolError, ToolResult
from ..logging_utils import ToolLogger
from ._helpers import _err, _handle_request_exc, _upstream_err
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
    GitHubServiceError,
)

logger = logging.getLogger("github-mcp-server")


def register_misc_tools(mcp: FastMCP) -> None:

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
        tlog = ToolLogger(logger, "list_branches")
        try:
            data = list_branches(owner, repo, page=page, per_page=perPage)
            tlog.success()
            return json.dumps(ToolResult(success=True, statusCode=200, data=data).model_dump(mode="json"))
        except GitHubServiceError as exc:
            tlog.failure(exc.code, exc.message)
            return json.dumps(ToolResult(success=False, statusCode=exc.http_status or 400, error=ToolError(code=exc.code, message=exc.message, details=exc.details)).model_dump(mode="json"))
        except Exception as exc:
            tlog.failure("INTERNAL_ERROR", str(exc))
            return json.dumps(ToolResult(success=False, statusCode=500, error=ToolError(code="INTERNAL_ERROR", message="Unexpected error.", details={"exception": str(exc)})).model_dump(mode="json"))

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
        tlog = ToolLogger(logger, "list_commits")
        try:
            data = list_commits(owner, repo, sha=sha, path=path, author=author, since=since, until=until, page=page, per_page=perPage)
            tlog.success()
            return json.dumps(ToolResult(success=True, statusCode=200, data=data).model_dump(mode="json"))
        except GitHubServiceError as exc:
            tlog.failure(exc.code, exc.message)
            return json.dumps(ToolResult(success=False, statusCode=exc.http_status or 400, error=ToolError(code=exc.code, message=exc.message, details=exc.details)).model_dump(mode="json"))
        except Exception as exc:
            tlog.failure("INTERNAL_ERROR", str(exc))
            return json.dumps(ToolResult(success=False, statusCode=500, error=ToolError(code="INTERNAL_ERROR", message="Unexpected error.", details={"exception": str(exc)})).model_dump(mode="json"))

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
        tlog = ToolLogger(logger, "get_commit")
        try:
            data = get_commit(owner, repo, sha, include_diff=include_diff)
            tlog.success()
            return json.dumps(ToolResult(success=True, statusCode=200, data=data).model_dump(mode="json"))
        except GitHubServiceError as exc:
            tlog.failure(exc.code, exc.message)
            return json.dumps(ToolResult(success=False, statusCode=exc.http_status or 400, error=ToolError(code=exc.code, message=exc.message, details=exc.details)).model_dump(mode="json"))
        except Exception as exc:
            tlog.failure("INTERNAL_ERROR", str(exc))
            return json.dumps(ToolResult(success=False, statusCode=500, error=ToolError(code="INTERNAL_ERROR", message="Unexpected error.", details={"exception": str(exc)})).model_dump(mode="json"))

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
        tlog = ToolLogger(logger, "get_file_contents")
        try:
            data = get_file_contents(owner, repo, path=path, ref=ref)
            tlog.success()
            return json.dumps(ToolResult(success=True, statusCode=200, data=data).model_dump(mode="json"))
        except GitHubServiceError as exc:
            tlog.failure(exc.code, exc.message)
            return json.dumps(ToolResult(success=False, statusCode=exc.http_status or 400, error=ToolError(code=exc.code, message=exc.message, details=exc.details)).model_dump(mode="json"))
        except Exception as exc:
            tlog.failure("INTERNAL_ERROR", str(exc))
            return json.dumps(ToolResult(success=False, statusCode=500, error=ToolError(code="INTERNAL_ERROR", message="Unexpected error.", details={"exception": str(exc)})).model_dump(mode="json"))

    @mcp.tool(
        name="list_tags",
        description="List all git tags in a repository with pagination support.",
    )
    def list_tags_tool(
        owner: str = Field(..., description="Repository owner name."),
        repo: str = Field(..., description="Repository name."),
        page: int = Field(1, description="Page number."),
        perPage: int = Field(30, description="Number of tags per page (1-100)."),
    ) -> str:
        tlog = ToolLogger(logger, "list_tags")
        try:
            data = list_tags(owner, repo, page=page, per_page=perPage)
            tlog.success()
            return json.dumps(ToolResult(success=True, statusCode=200, data=data).model_dump(mode="json"))
        except GitHubServiceError as exc:
            tlog.failure(exc.code, exc.message)
            return json.dumps(ToolResult(success=False, statusCode=exc.http_status or 400, error=ToolError(code=exc.code, message=exc.message, details=exc.details)).model_dump(mode="json"))
        except Exception as exc:
            tlog.failure("INTERNAL_ERROR", str(exc))
            return json.dumps(ToolResult(success=False, statusCode=500, error=ToolError(code="INTERNAL_ERROR", message="Unexpected error.", details={"exception": str(exc)})).model_dump(mode="json"))

    @mcp.tool(
        name="get_tag",
        description="Get detailed information about a specific git tag.",
    )
    def get_tag_tool(
        owner: str = Field(..., description="Repository owner name."),
        repo: str = Field(..., description="Repository name."),
        tag: str = Field(..., description="Tag name to retrieve."),
    ) -> str:
        tlog = ToolLogger(logger, "get_tag")
        try:
            data = get_tag(owner, repo, tag)
            tlog.success()
            return json.dumps(ToolResult(success=True, statusCode=200, data=data).model_dump(mode="json"))
        except GitHubServiceError as exc:
            tlog.failure(exc.code, exc.message)
            return json.dumps(ToolResult(success=False, statusCode=exc.http_status or 400, error=ToolError(code=exc.code, message=exc.message, details=exc.details)).model_dump(mode="json"))
        except Exception as exc:
            tlog.failure("INTERNAL_ERROR", str(exc))
            return json.dumps(ToolResult(success=False, statusCode=500, error=ToolError(code="INTERNAL_ERROR", message="Unexpected error.", details={"exception": str(exc)})).model_dump(mode="json"))

    @mcp.tool(
        name="get_latest_release",
        description="Get the latest release in a repository.",
    )
    def get_latest_release_tool(
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
    ) -> str:
        tlog = ToolLogger(logger, "get_latest_release")
        try:
            data = get_latest_release(owner, repo)
            tlog.success()
            return json.dumps(ToolResult(success=True, statusCode=200, data=data).model_dump(mode="json"))
        except GitHubServiceError as exc:
            tlog.failure(exc.code, exc.message)
            return json.dumps(ToolResult(success=False, statusCode=exc.http_status or 400, error=ToolError(code=exc.code, message=exc.message, details=exc.details)).model_dump(mode="json"))
        except Exception as exc:
            tlog.failure("INTERNAL_ERROR", str(exc))
            return json.dumps(ToolResult(success=False, statusCode=500, error=ToolError(code="INTERNAL_ERROR", message="Unexpected error.", details={"exception": str(exc)})).model_dump(mode="json"))

    @mcp.tool(
        name="list_releases",
        description="List releases in a repository.",
    )
    def list_releases_tool(
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        page: int = Field(1, description="Page number"),
        per_page: int = Field(30, description="Results per page"),
    ) -> str:
        tlog = ToolLogger(logger, "list_releases")
        try:
            data = list_releases(owner, repo, page=page, per_page=per_page)
            tlog.success()
            return json.dumps(ToolResult(success=True, statusCode=200, data=data).model_dump(mode="json"))
        except GitHubServiceError as exc:
            tlog.failure(exc.code, exc.message)
            return json.dumps(ToolResult(success=False, statusCode=exc.http_status or 400, error=ToolError(code=exc.code, message=exc.message, details=exc.details)).model_dump(mode="json"))
        except Exception as exc:
            tlog.failure("INTERNAL_ERROR", str(exc))
            return json.dumps(ToolResult(success=False, statusCode=500, error=ToolError(code="INTERNAL_ERROR", message="Unexpected error.", details={"exception": str(exc)})).model_dump(mode="json"))

    @mcp.tool(
        name="get_release_by_tag",
        description="Get a specific release by tag name.",
    )
    def get_release_by_tag_tool(
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        tag: str = Field(..., description="Tag name (e.g., 'v1.0.0')"),
    ) -> str:
        tlog = ToolLogger(logger, "get_release_by_tag")
        try:
            data = get_release_by_tag(owner, repo, tag)
            tlog.success()
            return json.dumps(ToolResult(success=True, statusCode=200, data=data).model_dump(mode="json"))
        except GitHubServiceError as exc:
            tlog.failure(exc.code, exc.message)
            return json.dumps(ToolResult(success=False, statusCode=exc.http_status or 400, error=ToolError(code=exc.code, message=exc.message, details=exc.details)).model_dump(mode="json"))
        except Exception as exc:
            tlog.failure("INTERNAL_ERROR", str(exc))
            return json.dumps(ToolResult(success=False, statusCode=500, error=ToolError(code="INTERNAL_ERROR", message="Unexpected error.", details={"exception": str(exc)})).model_dump(mode="json"))

    @mcp.tool(
        name="get_label",
        description="Get a specific label from a repository.",
    )
    def get_label_tool(
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        name: str = Field(..., description="Label name"),
    ) -> str:
        tlog = ToolLogger(logger, "get_label")
        try:
            data = get_label(owner, repo, name)
            tlog.success()
            return json.dumps(ToolResult(success=True, statusCode=200, data=data).model_dump(mode="json"))
        except GitHubServiceError as exc:
            tlog.failure(exc.code, exc.message)
            return json.dumps(ToolResult(success=False, statusCode=exc.http_status or 400, error=ToolError(code=exc.code, message=exc.message, details=exc.details)).model_dump(mode="json"))
        except Exception as exc:
            tlog.failure("INTERNAL_ERROR", str(exc))
            return json.dumps(ToolResult(success=False, statusCode=500, error=ToolError(code="INTERNAL_ERROR", message="Unexpected error.", details={"exception": str(exc)})).model_dump(mode="json"))

    @mcp.tool(
        name="get_me",
        description="Get details of the authenticated GitHub user.",
    )
    def get_me_tool() -> str:
        tlog = ToolLogger(logger, "get_me")
        try:
            data = get_me()
            tlog.success()
            return json.dumps(ToolResult(success=True, statusCode=200, data=data).model_dump(mode="json"))
        except GitHubServiceError as exc:
            tlog.failure(exc.code, exc.message)
            return json.dumps(ToolResult(success=False, statusCode=exc.http_status or 400, error=ToolError(code=exc.code, message=exc.message, details=exc.details)).model_dump(mode="json"))
        except Exception as exc:
            tlog.failure("INTERNAL_ERROR", str(exc))
            return json.dumps(ToolResult(success=False, statusCode=500, error=ToolError(code="INTERNAL_ERROR", message="Unexpected error.", details={"exception": str(exc)})).model_dump(mode="json"))

    @mcp.tool(
        name="get_branch_protection",
        description="Get branch protection rules for a specific branch.",
    )
    def get_branch_protection_tool(
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        branch: str = Field(..., description="Branch name"),
    ) -> str:
        tlog = ToolLogger(logger, "get_branch_protection")
        try:
            data = get_branch_protection(owner, repo, branch)
            tlog.success()
            return json.dumps(ToolResult(success=True, statusCode=200, data=data).model_dump(mode="json"))
        except GitHubServiceError as exc:
            tlog.failure(exc.code, exc.message)
            return json.dumps(ToolResult(success=False, statusCode=exc.http_status or 400, error=ToolError(code=exc.code, message=exc.message, details=exc.details)).model_dump(mode="json"))
        except Exception as exc:
            tlog.failure("INTERNAL_ERROR", str(exc))
            return json.dumps(ToolResult(success=False, statusCode=500, error=ToolError(code="INTERNAL_ERROR", message="Unexpected error.", details={"exception": str(exc)})).model_dump(mode="json"))

    @mcp.tool(
        name="set_branch_protection",
        description="Set (create or replace) branch protection rules for a branch.",
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
    ) -> str:
        tlog = ToolLogger(logger, "set_branch_protection")
        try:
            data = set_branch_protection(owner, repo, branch, enforce_admins=enforce_admins, required_status_checks=required_status_checks, required_pull_request_reviews=required_pull_request_reviews, restrictions=restrictions, required_linear_history=required_linear_history, allow_force_pushes=allow_force_pushes, allow_deletions=allow_deletions, block_creations=block_creations, required_conversation_resolution=required_conversation_resolution, lock_branch=lock_branch, allow_fork_syncing=allow_fork_syncing)
            tlog.success()
            return json.dumps(ToolResult(success=True, statusCode=200, data=data).model_dump(mode="json"))
        except GitHubServiceError as exc:
            tlog.failure(exc.code, exc.message)
            return json.dumps(ToolResult(success=False, statusCode=exc.http_status or 400, error=ToolError(code=exc.code, message=exc.message, details=exc.details)).model_dump(mode="json"))
        except Exception as exc:
            tlog.failure("INTERNAL_ERROR", str(exc))
            return json.dumps(ToolResult(success=False, statusCode=500, error=ToolError(code="INTERNAL_ERROR", message="Unexpected error.", details={"exception": str(exc)})).model_dump(mode="json"))

    @mcp.tool(
        name="delete_branch_protection",
        description="DESTRUCTIVE — REQUIRES EXPLICIT USER CONFIRMATION BEFORE CALLING. Delete branch protection rules for a specific branch.",
    )
    def delete_branch_protection_tool(
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        branch: str = Field(..., description="Branch name"),
    ) -> str:
        tlog = ToolLogger(logger, "delete_branch_protection")
        try:
            data = delete_branch_protection(owner, repo, branch)
            tlog.success()
            return json.dumps(ToolResult(success=True, statusCode=200, data=data).model_dump(mode="json"))
        except GitHubServiceError as exc:
            tlog.failure(exc.code, exc.message)
            return json.dumps(ToolResult(success=False, statusCode=exc.http_status or 400, error=ToolError(code=exc.code, message=exc.message, details=exc.details)).model_dump(mode="json"))
        except Exception as exc:
            tlog.failure("INTERNAL_ERROR", str(exc))
            return json.dumps(ToolResult(success=False, statusCode=500, error=ToolError(code="INTERNAL_ERROR", message="Unexpected error.", details={"exception": str(exc)})).model_dump(mode="json"))

    @mcp.tool(
        name="get_pull_request_review_protection",
        description="Get PR review requirements for a protected branch.",
    )
    def get_pr_review_protection(
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        branch: str = Field(..., description="Branch name"),
    ) -> str:
        tlog = ToolLogger(logger, "get_pull_request_review_protection")
        try:
            data = get_pull_request_review_protection(owner, repo, branch)
            tlog.success()
            return json.dumps(ToolResult(success=True, statusCode=200, data=data).model_dump(mode="json"))
        except GitHubServiceError as exc:
            tlog.failure(exc.code, exc.message)
            return json.dumps(ToolResult(success=False, statusCode=exc.http_status or 400, error=ToolError(code=exc.code, message=exc.message, details=exc.details)).model_dump(mode="json"))
        except Exception as exc:
            tlog.failure("INTERNAL_ERROR", str(exc))
            return json.dumps(ToolResult(success=False, statusCode=500, error=ToolError(code="INTERNAL_ERROR", message="Unexpected error.", details={"exception": str(exc)})).model_dump(mode="json"))

    @mcp.tool(
        name="update_pull_request_review_protection",
        description="Update PR review requirements for a protected branch.",
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
    ) -> str:
        tlog = ToolLogger(logger, "update_pull_request_review_protection")
        try:
            data = update_pull_request_review_protection(owner, repo, branch, dismiss_stale_reviews=dismiss_stale_reviews, require_code_owner_reviews=require_code_owner_reviews, required_approving_review_count=required_approving_review_count, require_last_push_approval=require_last_push_approval, dismissal_restrictions=dismissal_restrictions)
            tlog.success()
            return json.dumps(ToolResult(success=True, statusCode=200, data=data).model_dump(mode="json"))
        except GitHubServiceError as exc:
            tlog.failure(exc.code, exc.message)
            return json.dumps(ToolResult(success=False, statusCode=exc.http_status or 400, error=ToolError(code=exc.code, message=exc.message, details=exc.details)).model_dump(mode="json"))
        except Exception as exc:
            tlog.failure("INTERNAL_ERROR", str(exc))
            return json.dumps(ToolResult(success=False, statusCode=500, error=ToolError(code="INTERNAL_ERROR", message="Unexpected error.", details={"exception": str(exc)})).model_dump(mode="json"))

    @mcp.tool(
        name="delete_pull_request_review_protection",
        description="DESTRUCTIVE — REQUIRES EXPLICIT USER CONFIRMATION BEFORE CALLING. Remove PR review requirements from a protected branch.",
    )
    def delete_pr_review_protection(
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        branch: str = Field(..., description="Branch name"),
    ) -> str:
        tlog = ToolLogger(logger, "delete_pull_request_review_protection")
        try:
            data = delete_pull_request_review_protection(owner, repo, branch)
            tlog.success()
            return json.dumps(ToolResult(success=True, statusCode=200, data=data).model_dump(mode="json"))
        except GitHubServiceError as exc:
            tlog.failure(exc.code, exc.message)
            return json.dumps(ToolResult(success=False, statusCode=exc.http_status or 400, error=ToolError(code=exc.code, message=exc.message, details=exc.details)).model_dump(mode="json"))
        except Exception as exc:
            tlog.failure("INTERNAL_ERROR", str(exc))
            return json.dumps(ToolResult(success=False, statusCode=500, error=ToolError(code="INTERNAL_ERROR", message="Unexpected error.", details={"exception": str(exc)})).model_dump(mode="json"))

    @mcp.tool(
        name="list_repository_rulesets",
        description="List all rulesets for a repository.",
    )
    def list_repository_rulesets_tool(
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        includes_parents: bool = Field(True, description="Include parent rulesets"),
        per_page: int = Field(30, description="Results per page"),
        page: int = Field(1, description="Page number"),
    ) -> str:
        tlog = ToolLogger(logger, "list_repository_rulesets")
        try:
            data = list_repository_rulesets(owner, repo, includes_parents=includes_parents, per_page=per_page, page=page)
            tlog.success()
            return json.dumps(ToolResult(success=True, statusCode=200, data=data).model_dump(mode="json"))
        except GitHubServiceError as exc:
            tlog.failure(exc.code, exc.message)
            return json.dumps(ToolResult(success=False, statusCode=exc.http_status or 400, error=ToolError(code=exc.code, message=exc.message, details=exc.details)).model_dump(mode="json"))
        except Exception as exc:
            tlog.failure("INTERNAL_ERROR", str(exc))
            return json.dumps(ToolResult(success=False, statusCode=500, error=ToolError(code="INTERNAL_ERROR", message="Unexpected error.", details={"exception": str(exc)})).model_dump(mode="json"))

    @mcp.tool(
        name="get_repository_ruleset",
        description="Get a specific ruleset for a repository.",
    )
    def get_repository_ruleset_tool(
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        ruleset_id: int = Field(..., description="Ruleset ID"),
    ) -> str:
        tlog = ToolLogger(logger, "get_repository_ruleset")
        try:
            data = get_repository_ruleset(owner, repo, ruleset_id)
            tlog.success()
            return json.dumps(ToolResult(success=True, statusCode=200, data=data).model_dump(mode="json"))
        except GitHubServiceError as exc:
            tlog.failure(exc.code, exc.message)
            return json.dumps(ToolResult(success=False, statusCode=exc.http_status or 400, error=ToolError(code=exc.code, message=exc.message, details=exc.details)).model_dump(mode="json"))
        except Exception as exc:
            tlog.failure("INTERNAL_ERROR", str(exc))
            return json.dumps(ToolResult(success=False, statusCode=500, error=ToolError(code="INTERNAL_ERROR", message="Unexpected error.", details={"exception": str(exc)})).model_dump(mode="json"))

    @mcp.tool(
        name="create_repository_ruleset",
        description="Create a new ruleset for a repository.",
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
    ) -> str:
        tlog = ToolLogger(logger, "create_repository_ruleset")
        try:
            data = create_repository_ruleset(owner, repo, name, enforcement=enforcement, target=target, conditions=conditions, rules=rules, bypass_actors=bypass_actors)
            tlog.success()
            return json.dumps(ToolResult(success=True, statusCode=200, data=data).model_dump(mode="json"))
        except GitHubServiceError as exc:
            tlog.failure(exc.code, exc.message)
            return json.dumps(ToolResult(success=False, statusCode=exc.http_status or 400, error=ToolError(code=exc.code, message=exc.message, details=exc.details)).model_dump(mode="json"))
        except Exception as exc:
            tlog.failure("INTERNAL_ERROR", str(exc))
            return json.dumps(ToolResult(success=False, statusCode=500, error=ToolError(code="INTERNAL_ERROR", message="Unexpected error.", details={"exception": str(exc)})).model_dump(mode="json"))

    @mcp.tool(
        name="update_repository_ruleset",
        description="Update an existing ruleset for a repository.",
    )
    def update_repository_ruleset_tool(
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        ruleset_id: int = Field(..., description="Ruleset ID"),
        name: str | None = Field(None, description="New ruleset name"),
        enforcement: str | None = Field(None, description="active, evaluate, or disabled"),
        conditions: dict | None = Field(None, description="Updated conditions"),
        rules: list[dict] | None = Field(None, description="Updated rules"),
        bypass_actors: list[dict] | None = Field(None, description="Updated bypass actors"),
    ) -> str:
        tlog = ToolLogger(logger, "update_repository_ruleset")
        try:
            data = update_repository_ruleset(owner, repo, ruleset_id, name=name, enforcement=enforcement, conditions=conditions, rules=rules, bypass_actors=bypass_actors)
            tlog.success()
            return json.dumps(ToolResult(success=True, statusCode=200, data=data).model_dump(mode="json"))
        except GitHubServiceError as exc:
            tlog.failure(exc.code, exc.message)
            return json.dumps(ToolResult(success=False, statusCode=exc.http_status or 400, error=ToolError(code=exc.code, message=exc.message, details=exc.details)).model_dump(mode="json"))
        except Exception as exc:
            tlog.failure("INTERNAL_ERROR", str(exc))
            return json.dumps(ToolResult(success=False, statusCode=500, error=ToolError(code="INTERNAL_ERROR", message="Unexpected error.", details={"exception": str(exc)})).model_dump(mode="json"))

    @mcp.tool(
        name="delete_repository_ruleset",
        description="DESTRUCTIVE — REQUIRES EXPLICIT USER CONFIRMATION BEFORE CALLING. Delete a ruleset from a repository.",
    )
    def delete_repository_ruleset_tool(
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        ruleset_id: int = Field(..., description="Ruleset ID"),
    ) -> str:
        tlog = ToolLogger(logger, "delete_repository_ruleset")
        try:
            data = delete_repository_ruleset(owner, repo, ruleset_id)
            tlog.success()
            return json.dumps(ToolResult(success=True, statusCode=200, data=data).model_dump(mode="json"))
        except GitHubServiceError as exc:
            tlog.failure(exc.code, exc.message)
            return json.dumps(ToolResult(success=False, statusCode=exc.http_status or 400, error=ToolError(code=exc.code, message=exc.message, details=exc.details)).model_dump(mode="json"))
        except Exception as exc:
            tlog.failure("INTERNAL_ERROR", str(exc))
            return json.dumps(ToolResult(success=False, statusCode=500, error=ToolError(code="INTERNAL_ERROR", message="Unexpected error.", details={"exception": str(exc)})).model_dump(mode="json"))
