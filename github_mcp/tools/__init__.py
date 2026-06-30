from fastmcp import FastMCP
from .repo_tools import register_repo_tools
from .search_tools import register_search_tools
from .issue_tools import register_issue_tools
from .pr_tools import register_pr_tools
from .misc_tools import register_misc_tools


def register_tools(mcp: FastMCP) -> None:
    register_repo_tools(mcp)
    register_search_tools(mcp)
    register_issue_tools(mcp)
    register_pr_tools(mcp)
    register_misc_tools(mcp)
