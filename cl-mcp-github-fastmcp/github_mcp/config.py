import logging

GITHUB_API_BASE = "https://api.github.com"

TOOL_REQUIRED_SCOPES = {
    "ping": [],
    "get_repo": ["repo"],
    "list_branches": ["repo"],
    "search_repositories": ["repo"],
    "search_code": ["repo"],
    "search_users": ["repo"],
    "search_issues": ["repo"],
    "list_commits": ["repo"],
    "get_commit": ["repo"],
    "list_issues": ["repo"],
    "get_issue": ["repo"],
    "get_issue_comments": ["repo"],
    "get_file_contents": ["repo"],
    "list_org_repositories_by_contributor": ["repo"],
}


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )
