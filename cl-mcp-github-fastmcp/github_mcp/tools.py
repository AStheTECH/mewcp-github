import json
import logging

from fastmcp import FastMCP
from pydantic import Field

from .service import get_repo as get_repo_service

logger = logging.getLogger("github-mcp-server")


def register_tools(mcp: FastMCP) -> None:
    @mcp.tool(
        name="ping",
        description="Basic health check for CL GitHub MCP server.",
    )
    def ping() -> str:
        return json.dumps({"status": "ok", "server": "CL GitHub MCP Server"})

    @mcp.tool(
        name="get_repo",
        description="Get basic details for a GitHub repository.",
    )
    def get_repo(
        oauth_token: str = Field(..., description="GitHub token with repo read access"),
        owner: str = Field(..., description="Repository owner, for example octocat"),
        repo: str = Field(..., description="Repository name"),
    ) -> str:
        try:
            result = get_repo_service(oauth_token, owner, repo)
            return json.dumps(result)
        except Exception as exc:
            logger.error("Failed get_repo for %s/%s: %s", owner, repo, exc)
            return json.dumps({"error": str(exc)})
