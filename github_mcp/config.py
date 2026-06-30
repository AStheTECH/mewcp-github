import logging

SERVER_VERSION = "v1.0.0"
BREAKING_CHANGES: list[dict] = []

GITHUB_API_BASE = "https://api.github.com"
CONNECT_TIMEOUT = 5
READ_TIMEOUT = 30

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
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )
