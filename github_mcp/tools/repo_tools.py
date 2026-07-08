import json
import logging
from fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from ..schemas import (
    GetRepoData,
    GetRepoResult,
    UpdateRepositoryData,
    UpdateRepositoryUpdateData,
    UpdateRepositoryResult,
    CreateRepositoryData,
    CreateRepositoryResult,
    ForkRepositoryData,
    ForkRepositoryResult,
    CreateOrUpdateFileData,
    CreateOrUpdateFileResult,
    PushFilesData,
    PushFilesResult,
)
from ..logging_utils import ToolLogger
from ._helpers import _err, _handle_service_exc
from ..service import (
    get_repo as get_repo_service,
    update_repository,
    create_repository,
    fork_repository,
    create_or_update_file,
    push_files,
)

logger = logging.getLogger("github-mcp-server")


def register_repo_tools(mcp: FastMCP) -> None:

    @mcp.tool(
        name="get_repo",
        description="Get basic details for a GitHub repository.",
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True),
    )
    def get_repo(
        owner: str = Field(..., description="Repository owner, for example octocat"),
        repo: str = Field(..., description="Repository name"),
    ) -> GetRepoResult:
        tlog = ToolLogger(logger, "get_repo")
        try:
            data = get_repo_service(owner, repo)
            tlog.success()
            return GetRepoResult(success=True, statusCode=200, data=GetRepoData(**data))
        except Exception as exc:
            return _handle_service_exc(GetRepoResult, tlog, exc)

    @mcp.tool(
        name="update_repository",
        description=(
            "Updates repository metadata or renames a repository. Only the fields you provide are "
            "changed — others keep their current value. NOTE: this overwrites the current field "
            "values — the original state is not stored after the call. The response includes both "
            "the before and after state so you have a full record of what changed."
        ),
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=True),
    )
    def update_repository_tool(
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        name: str | None = Field(None, description="New repository name (to rename)"),
        description: str | None = Field(None, description="Repository description"),
        private: bool | None = Field(None, description="Make repository private/public"),
        default_branch: str | None = Field(None, description="Default branch name"),
    ) -> UpdateRepositoryResult:
        tlog = ToolLogger(logger, "update_repository")

        if name is None and description is None and private is None and default_branch is None:
            return _err(
                UpdateRepositoryResult,
                tlog,
                "VALIDATION_ERROR",
                "At least one field must be provided to update",
                400,
            )

        try:
            before = get_repo_service(owner, repo)
            after = update_repository(
                owner=owner, repo=repo, name=name, description=description, private=private, default_branch=default_branch,
            )
            tlog.success()
            return UpdateRepositoryResult(
                success=True,
                statusCode=200,
                data=UpdateRepositoryUpdateData(
                    before=GetRepoData(**before),
                    after=UpdateRepositoryData(**after),
                ),
            )
        except Exception as exc:
            return _handle_service_exc(UpdateRepositoryResult, tlog, exc)

    @mcp.tool(
        name="create_repository",
        description="Create a new GitHub repository in your personal account or an organization.",
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=True),
    )
    def create_repository_tool(
        name: str = Field(..., description="Repository name (required). Must be unique in account/organization."),
        description: str | None = Field(None, description="Repository description (optional)."),
        private: bool = Field(False, description="Make repository private (default: False for public)."),
        auto_init: bool = Field(False, description="Auto-initialize with README (default: False)."),
        gitignore_template: str | None = Field(None, description="Gitignore template name. Example: 'Python', 'Node'."),
        org: str | None = Field(None, description="Organization name to create repo in (optional)."),
    ) -> CreateRepositoryResult:
        tlog = ToolLogger(logger, "create_repository")
        try:
            data = create_repository(
                name=name, description=description, private=private, auto_init=auto_init,
                gitignore_template=gitignore_template, org=org,
            )
            tlog.success()
            return CreateRepositoryResult(success=True, statusCode=200, data=CreateRepositoryData(**data))
        except Exception as exc:
            return _handle_service_exc(CreateRepositoryResult, tlog, exc)

    @mcp.tool(
        name="fork_repository",
        description="Fork a repository to your personal account or an organization.",
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=True),
    )
    def fork_repository_tool(
        owner: str = Field(..., description="Original repository owner."),
        repo: str = Field(..., description="Original repository name."),
        org: str | None = Field(None, description="Organization name to fork into (optional)."),
    ) -> ForkRepositoryResult:
        tlog = ToolLogger(logger, "fork_repository")
        try:
            data = fork_repository(owner=owner, repo=repo, org=org)
            tlog.success()
            return ForkRepositoryResult(success=True, statusCode=200, data=ForkRepositoryData(**data))
        except Exception as exc:
            return _handle_service_exc(ForkRepositoryResult, tlog, exc)

    @mcp.tool(
        name="create_or_update_file",
        description="Create or update a file in a repository. Prevents accidental overwrites with SHA validation.",
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=True),
    )
    def create_or_update_file_tool(
        owner: str = Field(..., description="Repository owner name."),
        repo: str = Field(..., description="Repository name."),
        path: str = Field(..., description="File path in repository. Example: 'src/main.py'."),
        content: str = Field(..., description="File content to write."),
        message: str = Field(..., description="Commit message."),
        branch: str | None = Field(None, description="Target branch name (optional)."),
        sha: str | None = Field(None, description="File SHA for updates (optional)."),
    ) -> CreateOrUpdateFileResult:
        tlog = ToolLogger(logger, "create_or_update_file")
        try:
            data = create_or_update_file(
                owner=owner, repo=repo, path=path, content=content, message=message, branch=branch, sha=sha,
            )
            tlog.success()
            return CreateOrUpdateFileResult(success=True, statusCode=200, data=CreateOrUpdateFileData(**data))
        except Exception as exc:
            return _handle_service_exc(CreateOrUpdateFileResult, tlog, exc)

    @mcp.tool(
        name="push_files",
        description="Push multiple files to a repository in a single atomic commit.",
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=True),
    )
    def push_files_tool(
        owner: str = Field(..., description="Repository owner name."),
        repo: str = Field(..., description="Repository name."),
        files_json: str = Field(
            ...,
            description='JSON array of file objects with path and content keys. Example: \'[{"path": "file1.txt", "content": "hello"}]\'',
        ),
        message: str = Field(..., description="Commit message."),
        branch: str | None = Field(None, description="Target branch name (optional)."),
        author_name: str | None = Field(None, description="Author name (optional)."),
        author_email: str | None = Field(None, description="Author email (optional)."),
    ) -> PushFilesResult:
        tlog = ToolLogger(logger, "push_files")

        try:
            files = json.loads(files_json)
        except json.JSONDecodeError:
            return _err(PushFilesResult, tlog, "VALIDATION_ERROR", "files_json is not valid JSON", 400)

        try:
            data = push_files(
                owner=owner, repo=repo, files=files, message=message,
                branch=branch, author_name=author_name, author_email=author_email,
            )
            tlog.success()
            return PushFilesResult(success=True, statusCode=200, data=PushFilesData(**data))
        except Exception as exc:
            return _handle_service_exc(PushFilesResult, tlog, exc)
