import json
import logging
from fastmcp import FastMCP
from pydantic import Field

from ..schemas import ToolError, ToolResult
from ..logging_utils import ToolLogger
from ._helpers import _err, _handle_request_exc, _upstream_err
from ..service import (
    get_repo as get_repo_service,
    update_repository,
    create_repository,
    fork_repository,
    create_or_update_file,
    push_files,
    GitHubServiceError,
)

logger = logging.getLogger("github-mcp-server")


def register_repo_tools(mcp: FastMCP) -> None:

    @mcp.tool(
        name="get_repo",
        description="Get basic details for a GitHub repository.",
    )
    def get_repo(
        owner: str = Field(..., description="Repository owner, for example octocat"),
        repo: str = Field(..., description="Repository name"),
    ) -> str:
        tlog = ToolLogger(logger, "get_repo")
        try:
            result = get_repo_service(owner, repo)
            tlog.success()
            return json.dumps(ToolResult(success=True, statusCode=200, data=result).model_dump(mode="json"))
        except GitHubServiceError as exc:
            tlog.failure(exc.code, exc.message)
            return json.dumps(ToolResult(
                success=False,
                statusCode=exc.http_status or 400,
                error=ToolError(code=exc.code, message=exc.message, details=exc.details),
            ).model_dump(mode="json"))
        except Exception as exc:
            tlog.failure("INTERNAL_ERROR", str(exc))
            return json.dumps(ToolResult(
                success=False,
                statusCode=500,
                error=ToolError(code="INTERNAL_ERROR", message="Unexpected error while processing get_repo.", details={"exception": str(exc)}),
            ).model_dump(mode="json"))

    @mcp.tool(
        name="update_repository",
        description="Update repository metadata or rename a repository.",
    )
    def update_repository_tool(
        owner: str = Field(..., description="Repository owner"),
        repo: str = Field(..., description="Repository name"),
        name: str | None = Field(None, description="New repository name (to rename)"),
        description: str | None = Field(None, description="Repository description"),
        private: bool | None = Field(None, description="Make repository private/public"),
        default_branch: str | None = Field(None, description="Default branch name"),
    ) -> str:
        tlog = ToolLogger(logger, "update_repository")
        try:
            data = update_repository(
                owner=owner, repo=repo, name=name, description=description, private=private, default_branch=default_branch,
            )
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
                error=ToolError(code="INTERNAL_ERROR", message="Unexpected error while updating repository.", details={"exception": str(exc)}),
            ).model_dump(mode="json"))

    @mcp.tool(
        name="create_repository",
        description="Create a new GitHub repository in your personal account or an organization.",
    )
    def create_repository_tool(
        name: str = Field(..., description="Repository name (required). Must be unique in account/organization."),
        description: str | None = Field(None, description="Repository description (optional)."),
        private: bool = Field(False, description="Make repository private (default: False for public)."),
        auto_init: bool = Field(False, description="Auto-initialize with README (default: False)."),
        gitignore_template: str | None = Field(None, description="Gitignore template name. Example: 'Python', 'Node'."),
        org: str | None = Field(None, description="Organization name to create repo in (optional)."),
    ) -> str:
        tlog = ToolLogger(logger, "create_repository")
        try:
            data = create_repository(
                name=name, description=description, private=private, auto_init=auto_init,
                gitignore_template=gitignore_template, org=org,
            )
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
                error=ToolError(code="INTERNAL_ERROR", message="Unexpected error while creating repository.", details={"exception": str(exc)}),
            ).model_dump(mode="json"))

    @mcp.tool(
        name="fork_repository",
        description="Fork a repository to your personal account or an organization.",
    )
    def fork_repository_tool(
        owner: str = Field(..., description="Original repository owner."),
        repo: str = Field(..., description="Original repository name."),
        org: str | None = Field(None, description="Organization name to fork into (optional)."),
    ) -> str:
        tlog = ToolLogger(logger, "fork_repository")
        try:
            data = fork_repository(owner=owner, repo=repo, org=org)
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
                error=ToolError(code="INTERNAL_ERROR", message="Unexpected error while forking repository.", details={"exception": str(exc)}),
            ).model_dump(mode="json"))

    @mcp.tool(
        name="create_or_update_file",
        description="Create or update a file in a repository. Prevents accidental overwrites with SHA validation.",
    )
    def create_or_update_file_tool(
        owner: str = Field(..., description="Repository owner name."),
        repo: str = Field(..., description="Repository name."),
        path: str = Field(..., description="File path in repository. Example: 'src/main.py'."),
        content: str = Field(..., description="File content to write."),
        message: str = Field(..., description="Commit message."),
        branch: str | None = Field(None, description="Target branch name (optional)."),
        sha: str | None = Field(None, description="File SHA for updates (optional)."),
    ) -> str:
        tlog = ToolLogger(logger, "create_or_update_file")
        try:
            data = create_or_update_file(
                owner=owner, repo=repo, path=path, content=content, message=message, branch=branch, sha=sha,
            )
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
                error=ToolError(code="INTERNAL_ERROR", message="Unexpected error while creating or updating file.", details={"exception": str(exc)}),
            ).model_dump(mode="json"))

    @mcp.tool(
        name="push_files",
        description="Push multiple files to a repository in a single atomic commit.",
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
    ) -> str:
        tlog = ToolLogger(logger, "push_files")
        try:
            import json as json_lib
            files = json_lib.loads(files_json)
            data = push_files(
                owner=owner, repo=repo, files=files, message=message,
                branch=branch, author_name=author_name, author_email=author_email,
            )
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
                error=ToolError(code="INTERNAL_ERROR", message="Unexpected error while pushing files.", details={"exception": str(exc)}),
            ).model_dump(mode="json"))
