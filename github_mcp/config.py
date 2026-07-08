import logging
import os

SERVER_VERSION = "v2.0.0"
BREAKING_CHANGES: list[dict] = [
    {
        "version": "v2.0.0",
        "description": (
            "Tool responses changed from a JSON-encoded string to native typed "
            "structured objects. The `data` field on each tool response is now a "
            "typed model (one per tool) instead of an untyped dict serialized into "
            "a raw string."
        ),
    },
]

GITHUB_API_BASE = "https://api.github.com"
CONNECT_TIMEOUT = 5    # TCP connection — fixed across all servers
READ_TIMEOUT = 30      # GitHub REST API SLA is generous; 30s covers slow list/search endpoints

TOOL_REQUIRED_SCOPES = {
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
    "create_issue": ["repo"],
    "add_issue_comment": ["repo"],
    "update_issue": ["repo"],
    "get_file_contents": ["repo"],
    "list_org_repositories_by_contributor": ["repo"],
    "list_tags": ["repo"],
    "get_tag": ["repo"],
    "create_repository": ["repo"],
    "create_or_update_file": ["repo"],
    "fork_repository": ["repo"],
    "create_branch": ["repo"],
    "push_files": ["repo"],
    "pull_request_read": ["repo"],
    "list_pull_requests": ["repo"],
    "search_pull_requests": ["repo"],
    "create_pull_request": ["repo"],
    "update_pull_request": ["repo"],
    "merge_pull_request": ["repo"],
    "update_pull_request_branch": ["repo"],
    "pull_request_review_write": ["repo"],
    "add_reply_to_pull_request_comment": ["repo"],
    "get_latest_release": ["repo"],
    "list_releases": ["repo"],
    "get_release_by_tag": ["repo"],
    "get_label": ["repo"],
    "get_me": [],
    "sub_issue_write": ["repo"],
    "assign_copilot_to_issue": ["repo"],
    "request_copilot_review": ["repo"],
    "get_branch_protection": ["repo"],
    "set_branch_protection": ["repo"],
    "delete_branch_protection": ["repo"],
    "get_pull_request_review_protection": ["repo"],
    "update_pull_request_review_protection": ["repo"],
    "delete_pull_request_review_protection": ["repo"],
    "list_repository_rulesets": ["repo"],
    "get_repository_ruleset": ["repo"],
    "create_repository_ruleset": ["repo"],
    "update_repository_ruleset": ["repo"],
    "delete_repository_ruleset": ["repo"],
}


def configure_logging() -> None:
    log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
    try:
        from pythonjsonlogger import jsonlogger
        handler = logging.StreamHandler()
        handler.setFormatter(
            jsonlogger.JsonFormatter(fmt="%(asctime)s %(name)s %(levelname)s %(message)s")
        )
    except ImportError:
        handler = logging.StreamHandler()
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(log_level)
