**Your entire GitHub workflow, accessible through AI.**

A Model Context Protocol (MCP) server that exposes GitHub's API for repository management, code search, issue tracking, pull request workflows, and release management.


## Overview

The GitHub MCP Server provides comprehensive access to GitHub operations:

- Manage repositories, branches, commits, files, and releases across personal and organization accounts
- Full issue and pull request lifecycle — create, update, review, merge, and automate with Copilot
- Advanced search across repositories, code, users, issues, and pull requests
- Enforce quality gates with branch protection rules and repository rulesets

Perfect for:

- AI assistants that need to read, write, or manage GitHub repositories
- Automating code review, issue triage, and release workflows
- Building developer tools that integrate deeply with GitHub


## Tools

### Repository Operations

<details>
<summary><code>get_repo</code> — Get repository details</summary>

Returns basic information about a GitHub repository.

**Inputs:**
```
- `owner` (string, required) — Repository owner (user or organization)
- `repo` (string, required) — Repository name
```

**Output:**

```json
{
  "name": "my-repo",
  "full_name": "owner/my-repo",
  "description": "...",
  "default_branch": "main",
  "stargazers_count": 42,
  ...
}
```

</details>


<details>
<summary><code>list_branches</code> — List repository branches</summary>

Returns a paginated list of branches in a repository.

**Inputs:**
```
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `page` (int, optional) — Page number (default: 1)
- `per_page` (int, optional) — Results per page (max: 100, default: 30)
```

**Output:**

```json
{
  "branches": [{ "name": "main", "commit": { "sha": "abc123" } }, ...]
}
```

</details>


<details>
<summary><code>create_repository</code> — Create a new repository</summary>

Creates a new repository under the authenticated user or an organization.

**Inputs:**
```
- `name` (string, required) — Repository name
- `description` (string, optional) — Repository description
- `private` (bool, optional) — Make the repository private (default: false)
- `org` (string, optional) — Organization to create the repo under (omit for personal)
- `auto_init` (bool, optional) — Initialize with a README (default: false)
```

**Output:**

```json
{
  "full_name": "owner/new-repo",
  "html_url": "https://github.com/owner/new-repo",
  ...
}
```

</details>


<details>
<summary><code>fork_repository</code> — Fork a repository</summary>

Forks a repository to the authenticated user's account or an organization.

**Inputs:**
```
- `owner` (string, required) — Owner of the repository to fork
- `repo` (string, required) — Repository to fork
- `org` (string, optional) — Organization to fork into (omit for personal account)
```

**Output:**

```json
{
  "full_name": "your-username/forked-repo",
  "html_url": "https://github.com/your-username/forked-repo",
  ...
}
```

</details>


<details>
<summary><code>create_branch</code> — Create a new branch</summary>

Creates a new branch in a repository from a specified commit SHA.

**Inputs:**
```
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `branch` (string, required) — Name of the new branch
- `sha` (string, required) — Commit SHA to branch from
```

**Output:**

```json
{
  "ref": "refs/heads/new-branch",
  "object": { "sha": "abc123" }
}
```

</details>


### File & Commit Operations

<details>
<summary><code>get_file_contents</code> — Get file or directory contents</summary>

Returns the contents of a file or directory from a repository.

**Inputs:**
```
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `path` (string, required) — File or directory path
- `branch` (string, optional) — Branch, tag, or commit SHA (default: default branch)
```

**Output:**

```json
{
  "type": "file",
  "name": "README.md",
  "content": "base64-encoded-content",
  "sha": "abc123",
  ...
}
```

</details>


<details>
<summary><code>create_or_update_file</code> — Create or update a single file</summary>

Creates a new file or updates an existing file in a repository.

**Inputs:**
```
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `path` (string, required) — Path to the file
- `content` (string, required) — File content (base64 encoded)
- `message` (string, required) — Commit message
- `branch` (string, optional) — Branch to commit to
- `sha` (string, optional) — SHA of file being replaced (required for updates)
```

**Output:**

```json
{
  "commit": { "sha": "abc123", "message": "..." },
  "content": { "name": "file.txt", "path": "file.txt" }
}
```

</details>


<details>
<summary><code>push_files</code> — Push multiple files in one commit</summary>

Atomically pushes multiple files to a repository branch in a single commit.

**Inputs:**
```
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `branch` (string, required) — Branch to push to
- `files` (list, required) — List of file objects with path and content
- `message` (string, required) — Commit message
```

**Output:**

```json
{
  "sha": "new-commit-sha",
  "message": "Commit message"
}
```

</details>


<details>
<summary><code>list_commits</code> — List commits in a repository</summary>

Returns a paginated list of commits with optional filtering.

**Inputs:**
```
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `sha` (string, optional) — Branch or commit SHA to start from
- `path` (string, optional) — Filter commits by file path
- `author` (string, optional) — Filter by author username or email
- `since` (string, optional) — ISO 8601 datetime; only commits after this date
- `until` (string, optional) — ISO 8601 datetime; only commits before this date
- `page` (int, optional) — Page number
- `per_page` (int, optional) — Results per page (max: 100)
```

**Output:**

```json
{
  "commits": [{ "sha": "abc123", "commit": { "message": "..." }, "author": {...} }, ...]
}
```

</details>


<details>
<summary><code>get_commit</code> — Get a specific commit</summary>

Returns details of a single commit including the diff.

**Inputs:**
```
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `sha` (string, required) — Commit SHA
```

**Output:**

```json
{
  "sha": "abc123",
  "commit": { "message": "...", "author": {...} },
  "files": [{ "filename": "...", "additions": 5, "deletions": 2 }]
}
```

</details>


### Search Operations

<details>
<summary><code>search_repositories</code> — Search GitHub repositories</summary>

Searches GitHub repositories using query syntax with optional sorting.

**Inputs:**
```
- `query` (string, required) — Search query (supports GitHub search syntax)
- `sort` (string, optional) — Sort by: stars, forks, updated, or help-wanted-issues
- `order` (string, optional) — Sort direction: asc or desc
- `page` (int, optional) — Page number
- `per_page` (int, optional) — Results per page (max: 100)
```

**Output:**

```json
{
  "total_count": 1200,
  "items": [{ "full_name": "owner/repo", "stargazers_count": 500, ... }]
}
```

</details>


<details>
<summary><code>search_code</code> — Search code across GitHub</summary>

Searches code using GitHub's code search syntax.

**Inputs:**
```
- `query` (string, required) — Code search query (supports GitHub code search syntax)
- `page` (int, optional) — Page number
- `per_page` (int, optional) — Results per page (max: 100)
```

**Output:**

```json
{
  "total_count": 45,
  "items": [{ "name": "file.py", "repository": { "full_name": "owner/repo" }, ... }]
}
```

</details>


<details>
<summary><code>search_users</code> — Search GitHub users</summary>

Searches GitHub users by name, location, followers, or other criteria.

**Inputs:**
```
- `query` (string, required) — User search query
- `sort` (string, optional) — Sort by: followers, repositories, or joined
- `order` (string, optional) — Sort direction: asc or desc
- `page` (int, optional) — Page number
- `per_page` (int, optional) — Results per page (max: 100)
```

**Output:**

```json
{
  "total_count": 12,
  "items": [{ "login": "username", "html_url": "...", "followers": 300 }]
}
```

</details>


<details>
<summary><code>search_issues</code> — Search issues and pull requests</summary>

Searches issues (and PRs) across GitHub using search syntax.

**Inputs:**
```
- `query` (string, required) — Issue search query (supports GitHub issue search syntax)
- `sort` (string, optional) — Sort by: comments, reactions, created, updated
- `order` (string, optional) — Sort direction: asc or desc
- `page` (int, optional) — Page number
- `per_page` (int, optional) — Results per page (max: 100)
```

**Output:**

```json
{
  "total_count": 8,
  "items": [{ "title": "Bug: ...", "state": "open", "number": 42, ... }]
}
```

</details>


<details>
<summary><code>search_pull_requests</code> — Search pull requests</summary>

Searches pull requests across GitHub using search syntax.

**Inputs:**
```
- `query` (string, required) — PR search query (supports GitHub search syntax)
- `sort` (string, optional) — Sort by: comments, reactions, created, updated
- `order` (string, optional) — Sort direction: asc or desc
- `page` (int, optional) — Page number
- `per_page` (int, optional) — Results per page (max: 100)
```

**Output:**

```json
{
  "total_count": 3,
  "items": [{ "title": "Add feature", "state": "open", "number": 15, ... }]
}
```

</details>


### Issue Operations

<details>
<summary><code>list_issues</code> — List repository issues</summary>

Returns issues in a repository with optional state and label filtering.

**Inputs:**
```
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `state` (string, optional) — Issue state: open, closed, or all (default: open)
- `labels` (string, optional) — Comma-separated label names to filter by
- `assignee` (string, optional) — Filter by assignee username
- `milestone` (string, optional) — Filter by milestone number or title
- `page` (int, optional) — Page number
- `per_page` (int, optional) — Results per page (max: 100)
```

**Output:**

```json
{
  "issues": [{ "number": 42, "title": "Bug report", "state": "open", ... }]
}
```

</details>


<details>
<summary><code>get_issue</code> — Get a specific issue</summary>

Returns full details of a single issue.

**Inputs:**
```
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `issue_number` (int, required) — Issue number
```

**Output:**

```json
{
  "number": 42,
  "title": "Bug report",
  "body": "...",
  "state": "open",
  "labels": [...],
  ...
}
```

</details>


<details>
<summary><code>get_issue_comments</code> — List comments on an issue</summary>

Returns paginated comments for an issue or pull request.

**Inputs:**
```
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `issue_number` (int, required) — Issue number
- `page` (int, optional) — Page number
- `per_page` (int, optional) — Results per page (max: 100)
```

**Output:**

```json
{
  "comments": [{ "id": 1, "user": { "login": "..." }, "body": "..." }, ...]
}
```

</details>


<details>
<summary><code>create_issue</code> — Create a new issue</summary>

Creates a new issue in a repository.

**Inputs:**
```
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `title` (string, required) — Issue title
- `body` (string, optional) — Issue description (Markdown supported)
- `assignees` (list, optional) — List of usernames to assign
- `labels` (list, optional) — List of label names to apply
- `milestone` (int, optional) — Milestone number to associate
```

**Output:**

```json
{
  "number": 43,
  "title": "New issue",
  "html_url": "https://github.com/owner/repo/issues/43",
  ...
}
```

</details>


<details>
<summary><code>add_issue_comment</code> — Add a comment to an issue</summary>

Adds a comment to an issue or pull request.

**Inputs:**
```
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `issue_number` (int, required) — Issue or PR number
- `body` (string, required) — Comment text (Markdown supported)
```

**Output:**

```json
{
  "id": 101,
  "body": "Your comment here",
  "user": { "login": "..." }
}
```

</details>


<details>
<summary><code>update_issue</code> — Update an existing issue</summary>

Updates the title, body, state, assignees, labels, or milestone of an issue.

**Inputs:**
```
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `issue_number` (int, required) — Issue number
- `title` (string, optional) — New title
- `body` (string, optional) — New body
- `state` (string, optional) — New state: open or closed
- `assignees` (list, optional) — Replacement list of assignees
- `labels` (list, optional) — Replacement list of labels
- `milestone` (int, optional) — Milestone number (or null to unset)
```

**Output:**

```json
{
  "number": 42,
  "state": "closed",
  "title": "Updated title",
  ...
}
```

</details>


<details>
<summary><code>sub_issue_write</code> — Manage sub-issues</summary>

Adds, removes, or reprioritizes sub-issues within a parent issue.

**Inputs:**
```
- `operation` (string, required) — Operation: add, remove, or reprioritize
- `parent_issue_id` (int, required) — Node ID of the parent issue
- `sub_issue_id` (int, optional) — Node ID of the sub-issue (for add/remove)
- `after_id` (int, optional) — Sub-issue ID to insert after (for reprioritize)
```

**Output:**

```json
{
  "success": true,
  "parent_issue": { "number": 10, "sub_issues_count": 3 }
}
```

</details>


### Pull Request Operations

<details>
<summary><code>list_pull_requests</code> — List pull requests</summary>

Returns pull requests in a repository with optional filtering.

**Inputs:**
```
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `state` (string, optional) — PR state: open, closed, or all (default: open)
- `head` (string, optional) — Filter by head branch (format: user:branch)
- `base` (string, optional) — Filter by base branch
- `sort` (string, optional) — Sort by: created, updated, popularity, long-running
- `direction` (string, optional) — Sort direction: asc or desc
- `page` (int, optional) — Page number
- `per_page` (int, optional) — Results per page (max: 100)
```

**Output:**

```json
{
  "pull_requests": [{ "number": 15, "title": "Feature", "state": "open", ... }]
}
```

</details>


<details>
<summary><code>pull_request_read</code> — Get pull request data</summary>

Retrieves PR details, changed files, status checks, comments, or reviews depending on the operation.

**Inputs:**
```
- `operation` (string, required) — What to retrieve: details, files, status, comments, or reviews
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `pull_number` (int, required) — Pull request number
```

**Output:**

```json
{
  "number": 15,
  "title": "Add feature",
  "state": "open",
  "mergeable": true,
  ...
}
```

</details>


<details>
<summary><code>create_pull_request</code> — Create a pull request</summary>

Creates a new pull request from a head branch into a base branch.

**Inputs:**
```
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `title` (string, required) — PR title
- `head` (string, required) — Branch with changes (format: username:branch or just branch)
- `base` (string, required) — Branch to merge into
- `body` (string, optional) — PR description (Markdown supported)
- `draft` (bool, optional) — Create as draft PR (default: false)
- `maintainer_can_modify` (bool, optional) — Allow maintainers to push to head branch
```

**Output:**

```json
{
  "number": 16,
  "html_url": "https://github.com/owner/repo/pull/16",
  "state": "open",
  ...
}
```

</details>


<details>
<summary><code>update_pull_request</code> — Update a pull request</summary>

Updates the title, body, state, or base branch of a pull request.

**Inputs:**
```
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `pull_number` (int, required) — Pull request number
- `title` (string, optional) — New title
- `body` (string, optional) — New description
- `state` (string, optional) — New state: open or closed
- `base` (string, optional) — New base branch
```

**Output:**

```json
{
  "number": 16,
  "title": "Updated PR title",
  "state": "open"
}
```

</details>


<details>
<summary><code>merge_pull_request</code> — Merge a pull request</summary>

Merges a pull request using the specified merge method.

**Inputs:**
```
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `pull_number` (int, required) — Pull request number
- `commit_title` (string, optional) — Title for the merge commit
- `commit_message` (string, optional) — Message for the merge commit
- `merge_method` (string, optional) — Merge method: merge, squash, or rebase (default: merge)
```

**Output:**

```json
{
  "merged": true,
  "message": "Pull Request successfully merged",
  "sha": "merge-commit-sha"
}
```

</details>


<details>
<summary><code>update_pull_request_branch</code> — Update a PR branch with latest base</summary>

Updates a pull request branch with the latest changes from the base branch.

**Inputs:**
```
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `pull_number` (int, required) — Pull request number
```

**Output:**

```json
{
  "message": "Updating pull request branch.",
  "url": "..."
}
```

</details>


<details>
<summary><code>pull_request_review_write</code> — Manage PR reviews</summary>

Creates, submits, deletes reviews, or resolves review threads on a pull request.

**Inputs:**
```
- `operation` (string, required) — Operation: create, submit, delete, or resolve_thread
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `pull_number` (int, required) — Pull request number
- `review_id` (int, optional) — Review ID (required for submit/delete)
- `body` (string, optional) — Review comment body
- `event` (string, optional) — Review event: APPROVE, REQUEST_CHANGES, or COMMENT
- `thread_id` (string, optional) — Thread ID to resolve
```

**Output:**

```json
{
  "id": 200,
  "state": "APPROVED",
  "body": "LGTM!"
}
```

</details>


<details>
<summary><code>add_reply_to_pull_request_comment</code> — Reply to a PR review comment</summary>

Adds a reply to an existing review comment on a pull request.

**Inputs:**
```
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `pull_number` (int, required) — Pull request number
- `comment_id` (int, required) — ID of the comment to reply to
- `body` (string, required) — Reply text (Markdown supported)
```

**Output:**

```json
{
  "id": 202,
  "body": "Reply text",
  "user": { "login": "..." }
}
```

</details>


### Releases & Tags

<details>
<summary><code>list_tags</code> — List repository tags</summary>

Returns a paginated list of tags in a repository.

**Inputs:**
```
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `page` (int, optional) — Page number
- `per_page` (int, optional) — Results per page (max: 100)
```

**Output:**

```json
{
  "tags": [{ "name": "v1.0.0", "commit": { "sha": "abc123" } }, ...]
}
```

</details>


<details>
<summary><code>get_tag</code> — Get a specific tag</summary>

Returns details about a specific tag in a repository.

**Inputs:**
```
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `tag` (string, required) — Tag name
```

**Output:**

```json
{
  "name": "v1.0.0",
  "commit": { "sha": "abc123" },
  ...
}
```

</details>


<details>
<summary><code>list_releases</code> — List repository releases</summary>

Returns a list of releases published in a repository.

**Inputs:**
```
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `page` (int, optional) — Page number
- `per_page` (int, optional) — Results per page (max: 100)
```

**Output:**

```json
{
  "releases": [{ "tag_name": "v1.0.0", "name": "First release", "body": "..." }, ...]
}
```

</details>


<details>
<summary><code>get_release_by_tag</code> — Get a release by tag</summary>

Returns the release associated with a specific tag.

**Inputs:**
```
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `tag` (string, required) — Tag name of the release
```

**Output:**

```json
{
  "tag_name": "v1.2.0",
  "name": "Release v1.2.0",
  "body": "Release notes...",
  ...
}
```

</details>


<details>
<summary><code>get_latest_release</code> — Get the latest release</summary>

Returns the most recent non-prerelease, non-draft release in a repository.

**Inputs:**
```
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
```

**Output:**

```json
{
  "tag_name": "v2.0.0",
  "name": "Latest stable",
  "published_at": "2024-01-01T00:00:00Z",
  ...
}
```

</details>


### User & Organization Operations

<details>
<summary><code>get_me</code> — Get authenticated user info</summary>

Returns information about the currently authenticated GitHub user.

**Inputs:**
```
None
```

**Output:**

```json
{
  "login": "your-username",
  "name": "Your Name",
  "email": "you@example.com",
  ...
}
```

</details>


<details>
<summary><code>get_label</code> — Get a repository label</summary>

Returns details about a specific label in a repository.

**Inputs:**
```
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `name` (string, required) — Label name
```

**Output:**

```json
{
  "name": "bug",
  "color": "d73a4a",
  "description": "Something isn't working"
}
```

</details>


<details>
<summary><code>list_org_repositories_by_contributor</code> — Find org repos by contributor</summary>

Lists repositories within an organization where a specific user has contributed.

**Inputs:**
```
- `org` (string, required) — Organization name
- `username` (string, required) — GitHub username to search for contributions
```

**Output:**

```json
{
  "repositories": [{ "name": "repo-name", "full_name": "org/repo-name", ... }]
}
```

</details>


### GitHub Copilot Operations

<details>
<summary><code>assign_copilot_to_issue</code> — Assign Copilot to an issue</summary>

Assigns GitHub Copilot as an assignee to work on an issue, with optional custom instructions.

**Inputs:**
```
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `issue_number` (int, required) — Issue number
- `instructions` (string, optional) — Custom instructions for Copilot
```

**Output:**

```json
{
  "success": true,
  "issue_number": 42,
  "assignee": "copilot"
}
```

</details>


<details>
<summary><code>request_copilot_review</code> — Request a Copilot PR review</summary>

Requests GitHub Copilot to review a pull request.

**Inputs:**
```
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `pull_number` (int, required) — Pull request number
```

**Output:**

```json
{
  "success": true,
  "pull_number": 16,
  "reviewer": "copilot"
}
```

</details>


### Branch Protection & Rulesets

<details>
<summary><code>get_branch_protection</code> — Get branch protection rules</summary>

Returns all protection rules configured for a specific branch.

**Inputs:**
```
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `branch` (string, required) — Branch name
```

**Output:**

```json
{
  "url": "https://api.github.com/repos/owner/repo/branches/main/protection",
  "required_status_checks": { "strict": true, "contexts": ["ci/test"] },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": false,
    "required_approving_review_count": 1,
    "require_last_push_approval": false,
    "dismissal_restrictions": { "users": [], "teams": [] }
  },
  "restrictions": null,
  "required_linear_history": false,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "required_conversation_resolution": true
}
```

</details>


<details>
<summary><code>set_branch_protection</code> — Create or replace branch protection rules</summary>

Creates or fully replaces branch protection rules for a branch (PUT). Complex nested objects are passed as JSON strings.

**Inputs:**
```
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `branch` (string, required) — Branch to protect
- `enforce_admins` (bool, required) — Apply rules to administrators
- `required_status_checks_json` (string, optional) — JSON: {"strict": bool, "contexts": [...]}
- `required_pull_request_reviews_json` (string, optional) — JSON: {"required_approving_review_count": int, ...}
- `restrictions_json` (string, optional) — JSON: {"users": [...], "teams": [...], "apps": [...]}
- `required_linear_history` (bool, optional) — Require linear commit history (default: false)
- `allow_force_pushes` (bool, optional) — Allow force pushes (default: GitHub default)
- `allow_deletions` (bool, optional) — Allow branch deletion (default: false)
- `block_creations` (bool, optional) — Block matching ref creation (default: false)
- `required_conversation_resolution` (bool, optional) — Require resolved conversations (default: false)
- `lock_branch` (bool, optional) — Make branch read-only (default: false)
- `allow_fork_syncing` (bool, optional) — Allow forks to sync with upstream (default: false)
```

**Output:**

```json
{
  "url": "https://api.github.com/repos/owner/repo/branches/main/protection",
  "branch": "main",
  "enforce_admins": true,
  "required_linear_history": false,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "required_conversation_resolution": true,
  "lock_branch": false
}
```

</details>


<details>
<summary><code>delete_branch_protection</code> — Delete branch protection rules</summary>

Removes all protection rules from a branch.

**Inputs:**
```
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `branch` (string, required) — Branch name
```

**Output:**

```json
{
  "deleted": true,
  "branch": "main"
}
```

</details>


<details>
<summary><code>get_pull_request_review_protection</code> — Get PR review requirements</summary>

Returns the pull request review requirements configured for a protected branch.

**Inputs:**
```
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `branch` (string, required) — Branch name
```

**Output:**

```json
{
  "url": "https://api.github.com/repos/owner/repo/branches/main/protection/required_pull_request_reviews",
  "dismiss_stale_reviews": true,
  "require_code_owner_reviews": true,
  "required_approving_review_count": 2,
  "require_last_push_approval": false,
  "dismissal_restrictions": { "users": [], "teams": [] }
}
```

</details>


<details>
<summary><code>update_pull_request_review_protection</code> — Update PR review requirements</summary>

Updates only the specified PR review fields for a protected branch (PATCH).

**Inputs:**
```
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `branch` (string, required) — Branch name
- `dismiss_stale_reviews` (bool, optional) — Dismiss approvals on new commits
- `require_code_owner_reviews` (bool, optional) — Require review from code owners
- `required_approving_review_count` (int, optional) — Required approvals (0–6)
- `require_last_push_approval` (bool, optional) — Require approval from non-last-pusher
- `dismissal_restrictions_json` (string, optional) — JSON: {"users": [...], "teams": [...]}
```

**Output:**

```json
{
  "dismiss_stale_reviews": true,
  "require_code_owner_reviews": true,
  "required_approving_review_count": 2,
  "require_last_push_approval": false,
  "dismissal_restrictions": { "users": [], "teams": [] }
}
```

</details>


<details>
<summary><code>delete_pull_request_review_protection</code> — Remove PR review requirements</summary>

Removes pull request review requirements from a protected branch.

**Inputs:**
```
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `branch` (string, required) — Branch name
```

**Output:**

```json
{
  "deleted": true,
  "branch": "main"
}
```

</details>


<details>
<summary><code>list_repository_rulesets</code> — List repository rulesets</summary>

Returns all rulesets defined for a repository, optionally including those inherited from the parent organization.

**Inputs:**
```
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `includes_parents` (bool, optional) — Include parent org rulesets (default: true)
- `page` (int, optional) — Page number (default: 1)
- `per_page` (int, optional) — Results per page (default: 30)
```

**Output:**

```json
{
  "rulesets": [
    {
      "id": 42,
      "name": "Require PR reviews on main",
      "target": "branch",
      "source_type": "Repository",
      "enforcement": "active",
      "created_at": "2024-01-15T10:00:00Z",
      "updated_at": "2024-06-01T08:00:00Z"
    }
  ]
}
```

</details>


<details>
<summary><code>get_repository_ruleset</code> — Get a repository ruleset</summary>

Returns a specific ruleset with its full conditions, rules, and bypass actors.

**Inputs:**
```
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `ruleset_id` (int, required) — Ruleset ID
```

**Output:**

```json
{
  "id": 42,
  "name": "Require PR reviews on main",
  "target": "branch",
  "enforcement": "active",
  "conditions": { "ref_name": { "include": ["~DEFAULT_BRANCH"], "exclude": [] } },
  "rules": [{ "type": "pull_request", "parameters": { "required_approving_review_count": 1 } }],
  "bypass_actors": []
}
```

</details>


<details>
<summary><code>create_repository_ruleset</code> — Create a repository ruleset</summary>

Creates a new ruleset for a repository. Pass conditions, rules, and bypass actors as JSON strings.

**Inputs:**
```
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `name` (string, required) — Ruleset name
- `enforcement` (string, required) — active, evaluate, or disabled
- `target` (string, optional) — branch, tag, or push (default: branch)
- `conditions_json` (string, optional) — JSON ref conditions, e.g. {"ref_name": {"include": ["~DEFAULT_BRANCH"], "exclude": []}}
- `rules_json` (string, optional) — JSON array of rule objects, e.g. [{"type": "pull_request", "parameters": {...}}]
- `bypass_actors_json` (string, optional) — JSON array of bypass actors, e.g. [{"actor_id": 1, "actor_type": "Team", "bypass_mode": "always"}]
```

**Output:**

```json
{
  "id": 43,
  "name": "Block force pushes",
  "target": "branch",
  "enforcement": "active",
  "conditions": { "ref_name": { "include": ["~ALL"], "exclude": [] } },
  "rules": [{ "type": "non_fast_forward" }],
  "bypass_actors": []
}
```

</details>


<details>
<summary><code>update_repository_ruleset</code> — Update a repository ruleset</summary>

Replaces an existing ruleset (PUT). Only fields provided are sent to GitHub.

**Inputs:**
```
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `ruleset_id` (int, required) — Ruleset ID to update
- `name` (string, optional) — New ruleset name
- `enforcement` (string, optional) — active, evaluate, or disabled
- `target` (string, optional) — branch, tag, or push
- `conditions_json` (string, optional) — JSON ref conditions
- `rules_json` (string, optional) — JSON array of rule objects
- `bypass_actors_json` (string, optional) — JSON array of bypass actors
```

**Output:**

```json
{
  "id": 42,
  "name": "Require PR reviews on main",
  "enforcement": "active",
  "rules": [{ "type": "pull_request", "parameters": { "required_approving_review_count": 2 } }]
}
```

</details>


<details>
<summary><code>delete_repository_ruleset</code> — Delete a repository ruleset</summary>

Deletes a ruleset from a repository by ID.

**Inputs:**
```
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `ruleset_id` (int, required) — Ruleset ID to delete
```

**Output:**

```json
{
  "deleted": true,
  "ruleset_id": 42
}
```

</details>


## API Parameters Reference

<details>
<summary><strong>Pagination Parameters</strong></summary>

Most list endpoints support pagination:

- `page` — Page number (starting from 1)
- `per_page` — Results per page (default: 30, max: 100)

</details>

<details>
<summary><strong>GitHub Search Syntax</strong></summary>

Search tools support GitHub's full query syntax:

```
language:python stars:>1000        — Repos with Python, 1000+ stars
repo:owner/repo is:open label:bug  — Open bug issues in a specific repo
author:username created:>2024-01-01 — Commits by author after date
```

Full syntax reference: [GitHub Search Documentation](https://docs.github.com/en/search-github/searching-on-github)

</details>

<details>
<summary><strong>Date/Time Format</strong></summary>

All datetime parameters use ISO 8601 format:

```
Format: YYYY-MM-DDTHH:MM:SSZ
Example: 2024-01-15T10:30:00Z
```

</details>


## Troubleshooting

<details>
<summary><strong>Missing or Invalid Headers</strong></summary>

- **Cause:** OAuth token not provided in request headers or incorrect format
- **Solution:**
  1. Verify `Authorization: Bearer YOUR_TOKEN` and `X-Mewcp-Credential-Id: CREDENTIAL-ID` headers are present
  2. Check your GitHub OAuth credential is active in your MewCP account

</details>

<details>
<summary><strong>Insufficient Credits</strong></summary>

- **Cause:** API calls have exceeded your request limits
- **Solution:**
  1. Check credit usage in your Curious Layer dashboard
  2. Upgrade to a paid plan or add credits for higher limits
  3. Contact support for credit adjustments

</details>

<details>
<summary><strong>Credential Not Connected</strong></summary>

- **Cause:** No GitHub credential linked to your account
- **Solution:**
  1. Go to **Credentials** in your MewCP dashboard
  2. Connect your GitHub account via OAuth
  3. Retry the request with the correct `X-Mewcp-Credential-Id` header

</details>

<details>
<summary><strong>Malformed Request Payload</strong></summary>

- **Cause:** JSON payload is invalid or missing required fields
- **Solution:**
  1. Validate JSON syntax before sending
  2. Ensure all required tool parameters (owner, repo, etc.) are included
  3. Check parameter types match expected values

</details>

<details>
<summary><strong>Server Not Found</strong></summary>

- **Cause:** Incorrect server name in the API endpoint
- **Solution:**
  1. Verify endpoint format: `{server-name}/mcp/{tool-name}`
  2. Use correct server name from documentation
  3. Check available servers in your Curious Layer account

</details>

<details>
<summary><strong>GitHub API Error</strong></summary>

- **Cause:** Upstream GitHub API returned an error
- **Solution:**
  1. Check GitHub service status at [GitHub Status](https://githubstatus.com)
  2. Verify your OAuth token has the required scopes for the operation (e.g. `repo`, `read:org`)
  3. Review the error message returned in the response for specific details

</details>

---

### Resources

- **[GitHub REST API Documentation](https://docs.github.com/en/rest)** — Official API reference
- **[GitHub Search Syntax](https://docs.github.com/en/search-github/searching-on-github)** — Complete search query reference
- **[FastMCP Docs](https://gofastmcp.com/v2/getting-started/welcome)** — FastMCP specification
- **[FastMCP Credentials](https://pypi.org/project/fastmcp-credentials/)** — FastMCP Credentials package for credential handling
