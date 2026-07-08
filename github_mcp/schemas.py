from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict

# =============================================================================
# Base classes
# =============================================================================


class ToolError(BaseModel):
    """Error details returned by a tool."""

    code: str
    message: str
    details: Any = None


class ToolResult(BaseModel):
    """Base result model for all tool responses. No `data` field here —
    every tool defines its own typed result subclass with a typed `data`."""

    success: bool
    statusCode: int
    retriable: bool = False
    retry_after_seconds: int | None = None
    error: ToolError | None = None

    model_config = ConfigDict(extra="allow")


# =============================================================================
# repo_tools.py — get_repo, update_repository, create_repository,
#                  fork_repository, create_or_update_file, push_files
# =============================================================================


class GetRepoData(BaseModel):
    """Shape returned by service.get_repo()."""

    model_config = ConfigDict(extra="allow")

    id: int | None = None
    name: str | None = None
    full_name: str | None = None
    owner: dict[str, Any] | None = None
    html_url: str | None = None
    description: str | None = None
    private: bool | None = None
    fork: bool | None = None
    url: str | None = None
    default_branch: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
    stargazers_count: int | None = None
    language: str | None = None
    has_issues: bool | None = None
    has_downloads: bool | None = None
    forks_count: int | None = None


class GetRepoResult(ToolResult):
    data: GetRepoData | None = None


class UpdateRepositoryData(BaseModel):
    """Shape returned by service.update_repository() (the "after" state)."""

    model_config = ConfigDict(extra="allow")

    id: int | None = None
    name: str | None = None
    full_name: str | None = None
    html_url: str | None = None
    private: bool | None = None
    description: str | None = None
    default_branch: str | None = None


class UpdateRepositoryUpdateData(BaseModel):
    model_config = ConfigDict(extra="allow")

    before: GetRepoData
    after: UpdateRepositoryData


class UpdateRepositoryResult(ToolResult):
    data: UpdateRepositoryUpdateData | None = None


class CreateRepositoryData(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: int | None = None
    name: str | None = None
    full_name: str | None = None
    url: str | None = None
    html_url: str | None = None
    owner: dict[str, Any] | None = None
    private: bool | None = None
    created_at: str | None = None


class CreateRepositoryResult(ToolResult):
    data: CreateRepositoryData | None = None


class ForkRepositoryData(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: int | None = None
    name: str | None = None
    full_name: str | None = None
    url: str | None = None
    html_url: str | None = None
    owner: dict[str, Any] | None = None
    fork: bool | None = None


class ForkRepositoryResult(ToolResult):
    data: ForkRepositoryData | None = None


class CreateOrUpdateFileData(BaseModel):
    model_config = ConfigDict(extra="allow")

    content: dict[str, Any] | None = None
    commit: dict[str, Any] | None = None


class CreateOrUpdateFileResult(ToolResult):
    data: CreateOrUpdateFileData | None = None


class PushFilesData(BaseModel):
    model_config = ConfigDict(extra="allow")

    commit_sha: str | None = None
    tree_sha: str | None = None
    branch: str | None = None
    message: str | None = None
    url: str | None = None


class PushFilesResult(ToolResult):
    data: PushFilesData | None = None


# =============================================================================
# search_tools.py — search_repositories, search_code, search_users,
#                    search_issues, search_pull_requests
# =============================================================================


class RepositorySearchItem(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: int | None = None
    name: str | None = None
    full_name: str | None = None
    private: bool | None = None
    html_url: str | None = None
    description: str | None = None
    stars: int | None = None


class SearchRepositoriesData(BaseModel):
    model_config = ConfigDict(extra="allow")

    items: list[RepositorySearchItem] = []
    total_count: int = 0


class SearchRepositoriesResult(ToolResult):
    data: SearchRepositoriesData | None = None


class CodeSearchItem(BaseModel):
    model_config = ConfigDict(extra="allow")

    name: str | None = None
    path: str | None = None
    repository: str | None = None
    url: str | None = None


class SearchCodeData(BaseModel):
    model_config = ConfigDict(extra="allow")

    total_count: int = 0
    incomplete_results: bool = False
    items: list[CodeSearchItem] = []


class SearchCodeResult(ToolResult):
    data: SearchCodeData | None = None


class UserSearchItem(BaseModel):
    model_config = ConfigDict(extra="allow")

    login: str | None = None
    id: int | None = None
    profile_url: str | None = None
    avatar_url: str | None = None


class SearchUsersData(BaseModel):
    model_config = ConfigDict(extra="allow")

    total_count: int = 0
    incomplete_results: bool = False
    items: list[UserSearchItem] = []


class SearchUsersResult(ToolResult):
    data: SearchUsersData | None = None


class IssueSearchItem(BaseModel):
    model_config = ConfigDict(extra="allow")

    number: int | None = None
    title: str | None = None
    state: str | None = None
    body: str | None = None
    url: str | None = None
    comments: int | None = None
    user: str | None = None


class SearchIssuesData(BaseModel):
    model_config = ConfigDict(extra="allow")

    total_count: int = 0
    incomplete_results: bool = False
    items: list[IssueSearchItem] = []


class SearchIssuesResult(ToolResult):
    data: SearchIssuesData | None = None


class PullRequestSearchItem(BaseModel):
    model_config = ConfigDict(extra="allow")

    number: int | None = None
    title: str | None = None
    state: str | None = None
    url: str | None = None
    user: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
    comments: int | None = None


class SearchPullRequestsData(BaseModel):
    model_config = ConfigDict(extra="allow")

    total_count: int = 0
    incomplete_results: bool = False
    pull_requests: list[PullRequestSearchItem] = []
    page: int | None = None
    per_page: int | None = None


class SearchPullRequestsResult(ToolResult):
    data: SearchPullRequestsData | None = None


# =============================================================================
# issue_tools.py — list_issues, get_issue, get_issue_comments, create_issue,
#                   add_issue_comment, update_issue,
#                   list_org_repositories_by_contributor, sub_issue_write,
#                   assign_copilot_to_issue
# =============================================================================


class IssueListItem(BaseModel):
    model_config = ConfigDict(extra="allow")

    number: int | None = None
    title: str | None = None
    state: str | None = None
    url: str | None = None
    body: str | None = None
    user: str | None = None
    labels: list[str] = []
    created_at: str | None = None
    updated_at: str | None = None


class ListIssuesData(BaseModel):
    model_config = ConfigDict(extra="allow")

    issues: list[IssueListItem] = []
    count: int = 0


class ListIssuesResult(ToolResult):
    data: ListIssuesData | None = None


class GetIssueData(BaseModel):
    """Shape returned by service.get_issue()."""

    model_config = ConfigDict(extra="allow")

    number: int | None = None
    title: str | None = None
    body: str | None = None
    state: str | None = None
    state_reason: str | None = None
    labels: list[str] = []
    assignees: list[str] = []
    url: str | None = None
    user: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
    closed_at: str | None = None


class GetIssueResult(ToolResult):
    data: GetIssueData | None = None


class IssueCommentItem(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: int | None = None
    body: str | None = None
    url: str | None = None
    user: str | None = None
    created_at: str | None = None
    updated_at: str | None = None


class GetIssueCommentsData(BaseModel):
    model_config = ConfigDict(extra="allow")

    comments: list[IssueCommentItem] = []
    page: int | None = None
    per_page: int | None = None


class GetIssueCommentsResult(ToolResult):
    data: GetIssueCommentsData | None = None


class CreateIssueData(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: int | None = None
    number: int | None = None
    url: str | None = None
    title: str | None = None


class CreateIssueResult(ToolResult):
    data: CreateIssueData | None = None


class AddIssueCommentData(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: int | None = None
    url: str | None = None
    body: str | None = None
    user: str | None = None


class AddIssueCommentResult(ToolResult):
    data: AddIssueCommentData | None = None


class UpdateIssueData(BaseModel):
    """Shape returned by service.update_issue() (the "after" state)."""

    model_config = ConfigDict(extra="allow")

    id: int | None = None
    number: int | None = None
    url: str | None = None
    title: str | None = None
    state: str | None = None


class UpdateIssueUpdateData(BaseModel):
    model_config = ConfigDict(extra="allow")

    before: GetIssueData
    after: UpdateIssueData


class UpdateIssueResult(ToolResult):
    data: UpdateIssueUpdateData | None = None


class ContributorInfo(BaseModel):
    model_config = ConfigDict(extra="allow")

    username: str | None = None
    contributions: int = 0


class OrgContributedRepo(BaseModel):
    model_config = ConfigDict(extra="allow")

    repo: str | None = None
    full_name: str | None = None
    url: str | None = None
    private: bool | None = None
    description: str | None = None
    contributors: list[ContributorInfo] = []
    total_filtered_contributions: int = 0


class ListOrgRepositoriesByContributorData(BaseModel):
    model_config = ConfigDict(extra="allow")

    filter_contributors: list[str] = []
    organization: str | None = None
    repo_type_filter: str | None = None
    total_repos_with_filtered_contributors: int = 0
    repos: list[OrgContributedRepo] = []


class ListOrgRepositoriesByContributorResult(ToolResult):
    data: ListOrgRepositoriesByContributorData | None = None


class SubIssueWriteData(BaseModel):
    model_config = ConfigDict(extra="allow")

    method: str | None = None
    sub_issue_id: int | None = None
    success: bool | None = None
    message: str | None = None


class SubIssueWriteResult(ToolResult):
    data: SubIssueWriteData | None = None


class AssignCopilotToIssueData(BaseModel):
    model_config = ConfigDict(extra="allow")

    issue_number: int | None = None
    assigned: bool | None = None
    job_id: int | None = None
    status: str | None = None
    pull_request_url: str | None = None


class AssignCopilotToIssueResult(ToolResult):
    data: AssignCopilotToIssueData | None = None


# =============================================================================
# pr_tools.py — pull_request_read, list_pull_requests, create_pull_request,
#               update_pull_request, merge_pull_request,
#               update_pull_request_branch, pull_request_review_write,
#               add_reply_to_pull_request_comment, request_copilot_review
# =============================================================================


class PullRequestReadData(BaseModel):
    """Polymorphic shape covering all 5 `method` variants of
    service.pull_request_read() (get / get_files / get_status /
    get_comments / get_review_comments). Only the fields relevant to the
    method used will be populated; the rest stay None."""

    model_config = ConfigDict(extra="allow")

    # method="get"
    number: int | None = None
    title: str | None = None
    body: str | None = None
    state: str | None = None
    state_reason: str | None = None
    url: str | None = None
    user: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
    merged_at: str | None = None
    merged: bool | None = None
    merge_commit_sha: str | None = None
    head: dict[str, Any] | None = None
    base: dict[str, Any] | None = None
    draft: bool | None = None
    additions: int | None = None
    deletions: int | None = None
    changed_files: int | None = None
    commits: int | None = None
    labels: list[str] | None = None
    assignees: list[str] | None = None
    reviewers: list[str] | None = None

    # method="get_files"
    files: list[dict[str, Any]] | None = None
    total_files: int | None = None

    # method="get_status"
    sha: str | None = None
    total_count: int | None = None
    statuses: list[dict[str, Any]] | None = None

    # method="get_comments"
    comments: list[dict[str, Any]] | None = None
    total_comments: int | None = None

    # method="get_review_comments"
    review_comments: list[dict[str, Any]] | None = None
    total_review_comments: int | None = None

    # pagination (get_files / get_comments / get_review_comments)
    page: int | None = None
    per_page: int | None = None


class PullRequestReadResult(ToolResult):
    data: PullRequestReadData | None = None


class PullRequestListItem(BaseModel):
    model_config = ConfigDict(extra="allow")

    number: int | None = None
    title: str | None = None
    state: str | None = None
    url: str | None = None
    user: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
    draft: bool | None = None
    additions: int | None = None
    deletions: int | None = None
    changed_files: int | None = None


class ListPullRequestsData(BaseModel):
    model_config = ConfigDict(extra="allow")

    pull_requests: list[PullRequestListItem] = []
    total_count: int = 0
    page: int | None = None
    per_page: int | None = None


class ListPullRequestsResult(ToolResult):
    data: ListPullRequestsData | None = None


class CreatePullRequestData(BaseModel):
    model_config = ConfigDict(extra="allow")

    number: int | None = None
    title: str | None = None
    state: str | None = None
    draft: bool | None = None
    url: str | None = None
    head_branch: str | None = None
    base_branch: str | None = None
    created_at: str | None = None
    user: str | None = None


class CreatePullRequestResult(ToolResult):
    data: CreatePullRequestData | None = None


class UpdatePullRequestData(BaseModel):
    """Shape returned by service.update_pull_request() (the "after" state)."""

    model_config = ConfigDict(extra="allow")

    number: int | None = None
    title: str | None = None
    state: str | None = None
    draft: bool | None = None
    url: str | None = None
    updated_at: str | None = None


class UpdatePullRequestUpdateData(BaseModel):
    model_config = ConfigDict(extra="allow")

    before: PullRequestReadData
    after: UpdatePullRequestData


class UpdatePullRequestResult(ToolResult):
    data: UpdatePullRequestUpdateData | None = None


class MergePullRequestData(BaseModel):
    model_config = ConfigDict(extra="allow")

    merged: bool | None = None
    sha: str | None = None
    message: str | None = None


class MergePullRequestResult(ToolResult):
    data: MergePullRequestData | None = None


class UpdatePullRequestBranchData(BaseModel):
    model_config = ConfigDict(extra="allow")

    message: str | None = None
    url: str | None = None


class UpdatePullRequestBranchResult(ToolResult):
    data: UpdatePullRequestBranchData | None = None


class PullRequestReviewWriteData(BaseModel):
    """Polymorphic shape covering all `method` variants of
    service.pull_request_review_write() (create / submit_pending /
    delete_pending / resolve_thread / unresolve_thread)."""

    model_config = ConfigDict(extra="allow")

    # method="create"
    id: int | None = None
    node_id: str | None = None
    state: str | None = None
    body: str | None = None
    user: str | None = None
    submitted_at: str | None = None

    # method="delete_pending"
    deleted: bool | None = None
    review_id: int | None = None

    # method="resolve_thread" / "unresolve_thread"
    thread_id: str | None = None
    resolved: bool | None = None
    message: str | None = None


class PullRequestReviewWriteResult(ToolResult):
    data: PullRequestReviewWriteData | None = None


class AddReplyToPullRequestCommentData(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: int | None = None
    user: str | None = None
    body: str | None = None
    created_at: str | None = None
    url: str | None = None
    in_reply_to_id: int | None = None


class AddReplyToPullRequestCommentResult(ToolResult):
    data: AddReplyToPullRequestCommentData | None = None


class RequestCopilotReviewData(BaseModel):
    model_config = ConfigDict(extra="allow")

    pull_number: int | None = None
    requested: bool | None = None
    reviewer: str | None = None
    status: str | None = None


class RequestCopilotReviewResult(ToolResult):
    data: RequestCopilotReviewData | None = None


# =============================================================================
# misc_tools.py — list_branches, list_commits, get_commit, get_file_contents,
#                  list_tags, get_tag, get_latest_release, list_releases,
#                  get_release_by_tag, get_label, get_me,
#                  get_branch_protection, set_branch_protection,
#                  delete_branch_protection, get_pull_request_review_protection,
#                  update_pull_request_review_protection,
#                  delete_pull_request_review_protection,
#                  list_repository_rulesets, get_repository_ruleset,
#                  create_repository_ruleset, update_repository_ruleset,
#                  delete_repository_ruleset
# =============================================================================


class BranchItem(BaseModel):
    model_config = ConfigDict(extra="allow")

    name: str | None = None
    sha: str | None = None
    protected: bool = False


class ListBranchesData(BaseModel):
    model_config = ConfigDict(extra="allow")

    branches: list[BranchItem] = []


class ListBranchesResult(ToolResult):
    data: ListBranchesData | None = None


class CommitListItem(BaseModel):
    model_config = ConfigDict(extra="allow")

    sha: str | None = None
    message: str | None = None
    author: dict[str, Any] | None = None
    committer: dict[str, Any] | None = None
    date: str | None = None


class ListCommitsData(BaseModel):
    model_config = ConfigDict(extra="allow")

    commits: list[CommitListItem] = []


class ListCommitsResult(ToolResult):
    data: ListCommitsData | None = None


class GetCommitData(BaseModel):
    model_config = ConfigDict(extra="allow")

    sha: str | None = None
    message: str | None = None
    author: dict[str, Any] | None = None
    committer: dict[str, Any] | None = None
    date: str | None = None
    url: str | None = None
    files: list[dict[str, Any]] | None = None


class GetCommitResult(ToolResult):
    data: GetCommitData | None = None


class GetFileContentsData(BaseModel):
    """Polymorphic shape covering both directory and single-file responses
    from service.get_file_contents()."""

    model_config = ConfigDict(extra="allow")

    type: str | None = None

    # directory listing
    items: list[dict[str, Any]] | None = None

    # single file
    name: str | None = None
    path: str | None = None
    size: int | None = None
    url: str | None = None
    content: str | None = None
    encoding: str | None = None


class GetFileContentsResult(ToolResult):
    data: GetFileContentsData | None = None


class TagItem(BaseModel):
    model_config = ConfigDict(extra="allow")

    name: str | None = None
    commit: dict[str, Any] | None = None
    zipball_url: str | None = None
    tarball_url: str | None = None


class ListTagsData(BaseModel):
    model_config = ConfigDict(extra="allow")

    tags: list[TagItem] = []
    page: int | None = None
    per_page: int | None = None


class ListTagsResult(ToolResult):
    data: ListTagsData | None = None


class GetTagData(BaseModel):
    model_config = ConfigDict(extra="allow")

    ref: str | None = None
    node_id: str | None = None
    url: str | None = None
    object: dict[str, Any] | None = None


class GetTagResult(ToolResult):
    data: GetTagData | None = None


class GetLatestReleaseData(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: int | None = None
    tag_name: str | None = None
    name: str | None = None
    draft: bool | None = None
    prerelease: bool | None = None
    created_at: str | None = None
    published_at: str | None = None
    url: str | None = None
    body: str | None = None
    author: str | None = None


class GetLatestReleaseResult(ToolResult):
    data: GetLatestReleaseData | None = None


class ReleaseListItem(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: int | None = None
    tag_name: str | None = None
    name: str | None = None
    draft: bool | None = None
    prerelease: bool | None = None
    created_at: str | None = None
    published_at: str | None = None
    url: str | None = None
    author: str | None = None


class ListReleasesData(BaseModel):
    model_config = ConfigDict(extra="allow")

    releases: list[ReleaseListItem] = []
    total_count: int = 0
    page: int | None = None
    per_page: int | None = None


class ListReleasesResult(ToolResult):
    data: ListReleasesData | None = None


class GetReleaseByTagData(BaseModel):
    """Response shape is identical to GetLatestReleaseData — service.py's
    get_release_by_tag() and get_latest_release() build the same dict."""

    model_config = ConfigDict(extra="allow")

    id: int | None = None
    tag_name: str | None = None
    name: str | None = None
    draft: bool | None = None
    prerelease: bool | None = None
    created_at: str | None = None
    published_at: str | None = None
    url: str | None = None
    body: str | None = None
    author: str | None = None


class GetReleaseByTagResult(ToolResult):
    data: GetReleaseByTagData | None = None


class GetLabelData(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: int | None = None
    name: str | None = None
    color: str | None = None
    description: str | None = None
    url: str | None = None


class GetLabelResult(ToolResult):
    data: GetLabelData | None = None


class GetMeData(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: int | None = None
    login: str | None = None
    name: str | None = None
    email: str | None = None
    bio: str | None = None
    company: str | None = None
    location: str | None = None
    public_repos: int = 0
    followers: int = 0
    following: int = 0
    created_at: str | None = None
    updated_at: str | None = None
    avatar_url: str | None = None
    profile_url: str | None = None


class GetMeResult(ToolResult):
    data: GetMeData | None = None


class GetBranchProtectionData(BaseModel):
    model_config = ConfigDict(extra="allow")

    url: str | None = None
    required_status_checks: dict[str, Any] | None = None
    enforce_admins: bool | None = None
    required_pull_request_reviews: dict[str, Any] | None = None
    restrictions: dict[str, Any] | None = None
    required_linear_history: bool | None = None
    allow_force_pushes: bool | None = None
    allow_deletions: bool | None = None
    block_creations: bool | None = None
    required_conversation_resolution: bool | None = None
    required_signatures: bool | None = None
    lock_branch: bool | None = None
    allow_fork_syncing: bool | None = None


class GetBranchProtectionResult(ToolResult):
    data: GetBranchProtectionData | None = None


class SetBranchProtectionData(BaseModel):
    model_config = ConfigDict(extra="allow")

    url: str | None = None
    branch: str | None = None
    enforce_admins: bool | None = None
    required_linear_history: bool | None = None
    allow_force_pushes: bool | None = None
    allow_deletions: bool | None = None
    required_conversation_resolution: bool | None = None
    lock_branch: bool | None = None


class SetBranchProtectionResult(ToolResult):
    data: SetBranchProtectionData | None = None


class DeleteBranchProtectionData(BaseModel):
    model_config = ConfigDict(extra="allow")

    deleted: bool | None = None
    branch: str | None = None


class DeleteBranchProtectionResult(ToolResult):
    data: DeleteBranchProtectionData | None = None


class GetPullRequestReviewProtectionData(BaseModel):
    """Shape returned by both service.get_pull_request_review_protection()
    and service.update_pull_request_review_protection() — identical shape."""

    model_config = ConfigDict(extra="allow")

    url: str | None = None
    dismiss_stale_reviews: bool | None = None
    require_code_owner_reviews: bool | None = None
    required_approving_review_count: int | None = None
    require_last_push_approval: bool | None = None
    dismissal_restrictions: dict[str, Any] | None = None


class GetPullRequestReviewProtectionResult(ToolResult):
    data: GetPullRequestReviewProtectionData | None = None


class UpdatePullRequestReviewProtectionUpdateData(BaseModel):
    model_config = ConfigDict(extra="allow")

    before: GetPullRequestReviewProtectionData
    after: GetPullRequestReviewProtectionData


class UpdatePullRequestReviewProtectionResult(ToolResult):
    data: UpdatePullRequestReviewProtectionUpdateData | None = None


class DeletePullRequestReviewProtectionData(BaseModel):
    model_config = ConfigDict(extra="allow")

    deleted: bool | None = None
    branch: str | None = None


class DeletePullRequestReviewProtectionResult(ToolResult):
    data: DeletePullRequestReviewProtectionData | None = None


class RulesetListItem(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: int | None = None
    name: str | None = None
    target: str | None = None
    source_type: str | None = None
    enforcement: str | None = None
    node_id: str | None = None
    created_at: str | None = None
    updated_at: str | None = None


class ListRepositoryRulesetsData(BaseModel):
    model_config = ConfigDict(extra="allow")

    rulesets: list[RulesetListItem] = []
    page: int | None = None
    per_page: int | None = None


class ListRepositoryRulesetsResult(ToolResult):
    data: ListRepositoryRulesetsData | None = None


class GetRepositoryRulesetData(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: int | None = None
    name: str | None = None
    target: str | None = None
    source_type: str | None = None
    source: str | None = None
    enforcement: str | None = None
    conditions: dict[str, Any] | None = None
    rules: list[dict[str, Any]] = []
    bypass_actors: list[dict[str, Any]] = []
    node_id: str | None = None
    created_at: str | None = None
    updated_at: str | None = None


class GetRepositoryRulesetResult(ToolResult):
    data: GetRepositoryRulesetData | None = None


class CreateRepositoryRulesetData(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: int | None = None
    name: str | None = None
    target: str | None = None
    enforcement: str | None = None
    conditions: dict[str, Any] | None = None
    rules: list[dict[str, Any]] = []
    bypass_actors: list[dict[str, Any]] = []
    node_id: str | None = None
    created_at: str | None = None
    updated_at: str | None = None


class CreateRepositoryRulesetResult(ToolResult):
    data: CreateRepositoryRulesetData | None = None


class UpdateRepositoryRulesetData(BaseModel):
    """Shape returned by service.update_repository_ruleset() (the "after"
    state) — note it lacks source_type/source, unlike GetRepositoryRulesetData."""

    model_config = ConfigDict(extra="allow")

    id: int | None = None
    name: str | None = None
    target: str | None = None
    enforcement: str | None = None
    conditions: dict[str, Any] | None = None
    rules: list[dict[str, Any]] = []
    bypass_actors: list[dict[str, Any]] = []
    node_id: str | None = None
    created_at: str | None = None
    updated_at: str | None = None


class UpdateRepositoryRulesetUpdateData(BaseModel):
    model_config = ConfigDict(extra="allow")

    before: GetRepositoryRulesetData
    after: UpdateRepositoryRulesetData


class UpdateRepositoryRulesetResult(ToolResult):
    data: UpdateRepositoryRulesetUpdateData | None = None


class DeleteRepositoryRulesetData(BaseModel):
    model_config = ConfigDict(extra="allow")

    deleted: bool | None = None
    ruleset_id: int | None = None


class DeleteRepositoryRulesetResult(ToolResult):
    data: DeleteRepositoryRulesetData | None = None
