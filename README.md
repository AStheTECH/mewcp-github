
A Model Context Protocol (MCP) server that exposes GitHub's API for repository management, search, collaboration workflows, and automation tasks.

---

## Overview

The GitHub MCP Server provides stateless, multi-user GitHub API access through 40+ MCP tools:

- Repository, branch, commit, and file operations
- Issues and pull request lifecycle management
- Search, releases, labels, and Copilot workflow automation

Perfect for:

- AI-driven code maintenance and repository automation
- Engineering workflow orchestration across GitHub resources
- Building custom assistants for issue triage and PR operations

---

## Tools

<details>
<summary><code>get_repo</code> — Get repository details</summary>

Fetches core metadata for a repository, including owner, visibility, stars, and default branch.

**Inputs:**

- `oauth_token` (object, required) — GitHub token payload `{ "token": "...", "scopes": ["repo"] }`
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name

**Output:**

```json
{
	"ok": true,
	"data": {
		"full_name": "owner/repo",
		"default_branch": "main",
		"private": false
	}
}
```

**Usage Example:**

```bash
POST /mcp/cl-github-mcp-server/get_repo

{
	"oauth_token": {"token": "${GITHUB_TOKEN}", "scopes": ["repo"]},
	"owner": "github",
	"repo": "docs"
}
```

</details>

<details>
<summary><code>list_branches</code> — List repository branches</summary>

Returns paginated branch metadata for a repository.

**Inputs:**

- `oauth_token` (object, required) — GitHub token payload
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `page` (integer, optional) — Page number
- `perPage` (integer, optional) — Items per page

**Output:**

```json
{
	"ok": true,
	"data": [
		{"name": "main", "sha": "abc123", "protected": true}
	]
}
```

**Usage Example:**

```bash
POST /mcp/cl-github-mcp-server/list_branches

{
	"oauth_token": {"token": "${GITHUB_TOKEN}", "scopes": ["repo"]},
	"owner": "github",
	"repo": "docs",
	"page": 1,
	"perPage": 30
}
```

</details>

<details>
<summary><code>search_repositories</code> — Search GitHub repositories</summary>

Searches repositories by query with sorting and pagination.

**Inputs:**

- `oauth_token` (object, required) — GitHub token payload
- `query` (string, required) — Search query
- `sort` (string, optional) — `stars`, `forks`, `updated`
- `order` (string, optional) — `asc` or `desc`
- `page` (integer, optional) — Page number
- `perPage` (integer, optional) — Items per page

**Output:**

```json
{
	"ok": true,
	"data": {
		"total_count": 123,
		"items": [{"full_name": "owner/repo", "description": "..."}]
	}
}
```

**Usage Example:**

```bash
POST /mcp/cl-github-mcp-server/search_repositories

{
	"oauth_token": {"token": "${GITHUB_TOKEN}", "scopes": ["repo"]},
	"query": "topic:mcp language:python",
	"sort": "stars",
	"order": "desc"
}
```

</details>

<details>
<summary><code>search_code</code> — Search code across GitHub</summary>

Performs precise code search using GitHub query syntax.

**Inputs:**

- `oauth_token` (object, required) — GitHub token payload
- `query` (string, required) — Code search query
- `sort` (string, optional) — `indexed`
- `order` (string, optional) — `asc` or `desc`
- `page` (integer, optional) — Page number
- `perPage` (integer, optional) — Items per page

**Output:**

```json
{
	"ok": true,
	"data": {
		"total_count": 42,
		"items": [{"repository": "owner/repo", "path": "src/main.py"}]
	}
}
```

**Usage Example:**

```bash
POST /mcp/cl-github-mcp-server/search_code

{
	"oauth_token": {"token": "${GITHUB_TOKEN}", "scopes": ["repo"]},
	"query": "path:github_mcp class GitHubServiceError",
	"page": 1,
	"perPage": 20
}
```

</details>

<details>
<summary><code>search_users</code> — Search GitHub users</summary>

Finds users by profile attributes and query filters.

**Inputs:**

- `oauth_token` (object, required) — GitHub token payload
- `query` (string, required) — User search query
- `sort` (string, optional) — `followers`, `repositories`, `joined`
- `order` (string, optional) — `asc` or `desc`
- `page` (integer, optional) — Page number
- `perPage` (integer, optional) — Items per page

**Output:**

```json
{
	"ok": true,
	"data": {
		"items": [{"login": "octocat", "profile_url": "https://github.com/octocat"}]
	}
}
```

**Usage Example:**

```bash
POST /mcp/cl-github-mcp-server/search_users

{
	"oauth_token": {"token": "${GITHUB_TOKEN}", "scopes": ["repo"]},
	"query": "location:berlin followers:>100"
}
```

</details>

<details>
<summary><code>search_issues</code> — Search issues and pull requests</summary>

Searches issues/PRs globally or scoped to a repository.

**Inputs:**

- `oauth_token` (object, required) — GitHub token payload
- `query` (string, required) — Issue search query
- `sort` (string, optional) — `updated`, `created`, `comments`
- `order` (string, optional) — `asc` or `desc`
- `owner` (string, optional) — Repository owner (requires `repo`)
- `repo` (string, optional) — Repository name (requires `owner`)

**Output:**

```json
{
	"ok": true,
	"data": {
		"items": [{"number": 12, "title": "Bug report", "state": "open"}]
	}
}
```

**Usage Example:**

```bash
POST /mcp/cl-github-mcp-server/search_issues

{
	"oauth_token": {"token": "${GITHUB_TOKEN}", "scopes": ["repo"]},
	"query": "is:open label:bug",
	"owner": "github",
	"repo": "docs"
}
```

</details>

<details>
<summary><code>list_commits</code> — List repository commits</summary>

Lists commits with optional filters such as author, date range, path, and SHA.

**Inputs:**

- `oauth_token` (object, required) — GitHub token payload
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `sha` (string, optional) — Branch or commit SHA
- `author` (string, optional) — Author login
- `since` (string, optional) — ISO date

**Output:**

```json
{
	"ok": true,
	"data": [
		{"sha": "abc123", "message": "feat: add endpoint", "author": "octocat"}
	]
}
```

**Usage Example:**

```bash
POST /mcp/cl-github-mcp-server/list_commits

{
	"oauth_token": {"token": "${GITHUB_TOKEN}", "scopes": ["repo"]},
	"owner": "github",
	"repo": "docs",
	"page": 1,
	"perPage": 30
}
```

</details>

<details>
<summary><code>get_commit</code> — Get commit details</summary>

Fetches one commit and optionally includes changed files in the response.

**Inputs:**

- `oauth_token` (object, required) — GitHub token payload
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `sha` (string, required) — Commit SHA
- `include_diff` (boolean, optional) — Include file diff data

**Output:**

```json
{
	"ok": true,
	"data": {
		"sha": "abc123",
		"message": "fix: handle null scope",
		"files": [{"filename": "github_mcp/service.py", "status": "modified"}]
	}
}
```

**Usage Example:**

```bash
POST /mcp/cl-github-mcp-server/get_commit

{
	"oauth_token": {"token": "${GITHUB_TOKEN}", "scopes": ["repo"]},
	"owner": "github",
	"repo": "docs",
	"sha": "abc123",
	"include_diff": true
}
```

</details>

<details>
<summary><code>list_issues</code> — List repository issues</summary>

Returns issues with filters for state, labels, and pagination.

**Inputs:**

- `oauth_token` (object, required) — GitHub token payload
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `state` (string, optional) — `open`, `closed`, `all`
- `labels` (string, optional) — Comma-separated labels

**Output:**

```json
{
	"ok": true,
	"data": {
		"issues": [{"number": 101, "title": "Improve docs", "state": "open"}],
		"count": 1
	}
}
```

**Usage Example:**

```bash
POST /mcp/cl-github-mcp-server/list_issues

{
	"oauth_token": {"token": "${GITHUB_TOKEN}", "scopes": ["repo"]},
	"owner": "github",
	"repo": "docs",
	"state": "open"
}
```

</details>

<details>
<summary><code>get_issue</code> — Get issue details</summary>

Retrieves full metadata for a single issue.

**Inputs:**

- `oauth_token` (object, required) — GitHub token payload
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `issue_number` (integer, required) — Issue number

**Output:**

```json
{
	"ok": true,
	"data": {
		"number": 101,
		"title": "Improve docs",
		"state": "open",
		"labels": ["documentation"]
	}
}
```

**Usage Example:**

```bash
POST /mcp/cl-github-mcp-server/get_issue

{
	"oauth_token": {"token": "${GITHUB_TOKEN}", "scopes": ["repo", "public_repo"]},
	"owner": "github",
	"repo": "docs",
	"issue_number": 101
}
```

</details>

<details>
<summary><code>get_issue_comments</code> — Get issue comments</summary>

Lists comments on a single issue with pagination support.

**Inputs:**

- `oauth_token` (object, required) — GitHub token payload
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `issue_number` (integer, required) — Issue number
- `page` (integer, optional) — Page number
- `perPage` (integer, optional) — Results per page

**Output:**

```json
{
	"ok": true,
	"data": {
		"comments": [{"id": 1, "body": "Looks good", "user": "octocat"}],
		"page": 1,
		"per_page": 30
	}
}
```

**Usage Example:**

```bash
POST /mcp/cl-github-mcp-server/get_issue_comments

{
	"oauth_token": {"token": "${GITHUB_TOKEN}", "scopes": ["repo"]},
	"owner": "github",
	"repo": "docs",
	"issue_number": 101
}
```

</details>

<details>
<summary><code>create_issue</code> — Create issue</summary>

Creates a repository issue with optional body, assignees, labels, and milestone.

**Inputs:**

- `oauth_token` (object, required) — GitHub token payload
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `title` (string, required) — Issue title
- `body` (string, optional) — Issue body
- `labels` (array, optional) — Label names

**Output:**

```json
{
	"ok": true,
	"data": {"id": 12345, "number": 102, "url": "https://github.com/owner/repo/issues/102"}
}
```

**Usage Example:**

```bash
POST /mcp/cl-github-mcp-server/create_issue

{
	"oauth_token": {"token": "${GITHUB_TOKEN}", "scopes": ["repo"]},
	"owner": "github",
	"repo": "docs",
	"title": "Add API pagination examples",
	"labels": ["documentation"]
}
```

</details>

<details>
<summary><code>add_issue_comment</code> — Add issue/PR comment</summary>

Adds a markdown comment to an issue or pull request.

**Inputs:**

- `oauth_token` (object, required) — GitHub token payload
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `issue_number` (integer, required) — Issue/PR number
- `body` (string, required) — Comment body

**Output:**

```json
{
	"ok": true,
	"data": {"id": 9876, "url": "https://github.com/owner/repo/issues/101#issuecomment-1"}
}
```

**Usage Example:**

```bash
POST /mcp/cl-github-mcp-server/add_issue_comment

{
	"oauth_token": {"token": "${GITHUB_TOKEN}", "scopes": ["repo"]},
	"owner": "github",
	"repo": "docs",
	"issue_number": 101,
	"body": "Thanks, I can work on this."
}
```

</details>

<details>
<summary><code>update_issue</code> — Update issue fields</summary>

Updates issue title, body, state, labels, assignees, and milestone.

**Inputs:**

- `oauth_token` (object, required) — GitHub token payload
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `issue_number` (integer, required) — Issue number
- `state` (string, optional) — `open` or `closed`
- `state_reason` (string, optional) — `completed` or `not_planned`

**Output:**

```json
{
	"ok": true,
	"data": {"number": 101, "title": "Improve docs", "state": "closed"}
}
```

**Usage Example:**

```bash
POST /mcp/cl-github-mcp-server/update_issue

{
	"oauth_token": {"token": "${GITHUB_TOKEN}", "scopes": ["repo"]},
	"owner": "github",
	"repo": "docs",
	"issue_number": 101,
	"state": "closed",
	"state_reason": "completed"
}
```

</details>

<details>
<summary><code>get_file_contents</code> — Get repository file/directory content</summary>

Returns file content or directory listing for a path and ref.

**Inputs:**

- `oauth_token` (object, required) — GitHub token payload
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `path` (string, optional) — File or directory path
- `ref` (string, optional) — Branch, tag, or commit SHA

**Output:**

```json
{
	"ok": true,
	"data": {"type": "file", "name": "README.md", "encoding": "base64"}
}
```

**Usage Example:**

```bash
POST /mcp/cl-github-mcp-server/get_file_contents

{
	"oauth_token": {"token": "${GITHUB_TOKEN}", "scopes": ["repo"]},
	"owner": "github",
	"repo": "docs",
	"path": "/README.md",
	"ref": "main"
}
```

</details>

<details>
<summary><code>list_org_repositories_by_contributor</code> — Find org repositories by contributor</summary>

Finds organization repositories where one or more contributors have commit history.

**Inputs:**

- `oauth_token` (object, required) — GitHub token payload
- `org` (string, required) — Organization login
- `contributor_usernames` (string, required) — Comma-separated usernames
- `repo_type` (string, optional) — `all`, `public`, or `private`

**Output:**

```json
{
	"ok": true,
	"data": {"org": "github", "repositories": [{"name": "docs", "contributors": ["octocat"]}]}
}
```

**Usage Example:**

```bash
POST /mcp/cl-github-mcp-server/list_org_repositories_by_contributor

{
	"oauth_token": {"token": "${GITHUB_TOKEN}", "scopes": ["repo", "read:org"]},
	"org": "github",
	"contributor_usernames": "octocat,hubot",
	"repo_type": "all"
}
```

</details>

<details>
<summary><code>list_tags</code> — List repository tags</summary>

Returns tag names, commit references, and archive URLs.

**Inputs:**

- `oauth_token` (object, required) — GitHub token payload
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `page` (integer, optional) — Page number
- `perPage` (integer, optional) — Results per page

**Output:**

```json
{
	"ok": true,
	"data": {"tags": [{"name": "v1.0.0", "commit": {"sha": "abc123"}}]}
}
```

**Usage Example:**

```bash
POST /mcp/cl-github-mcp-server/list_tags

{
	"oauth_token": {"token": "${GITHUB_TOKEN}", "scopes": ["repo"]},
	"owner": "github",
	"repo": "docs"
}
```

</details>

<details>
<summary><code>get_tag</code> — Get tag details</summary>

Fetches metadata for one git tag reference.

**Inputs:**

- `oauth_token` (object, required) — GitHub token payload
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `tag` (string, required) — Tag name

**Output:**

```json
{
	"ok": true,
	"data": {"ref": "refs/tags/v1.0.0", "object": {"sha": "abc123"}}
}
```

**Usage Example:**

```bash
POST /mcp/cl-github-mcp-server/get_tag

{
	"oauth_token": {"token": "${GITHUB_TOKEN}", "scopes": ["repo"]},
	"owner": "github",
	"repo": "docs",
	"tag": "v1.0.0"
}
```

</details>

<details>
<summary><code>create_repository</code> — Create repository</summary>

Creates a repository in a personal account or organization.

**Inputs:**

- `oauth_token` (object, required) — GitHub token payload
- `name` (string, required) — Repository name
- `description` (string, optional) — Repository description
- `private` (boolean, optional) — Private visibility
- `org` (string, optional) — Organization target

**Output:**

```json
{
	"ok": true,
	"data": {"id": 2222, "full_name": "owner/new-repo", "private": true}
}
```

**Usage Example:**

```bash
POST /mcp/cl-github-mcp-server/create_repository

{
	"oauth_token": {"token": "${GITHUB_TOKEN}", "scopes": ["repo"]},
	"name": "cl-github-mcp-demo",
	"description": "Demo repository",
	"private": true,
	"auto_init": true
}
```

</details>

<details>
<summary><code>create_or_update_file</code> — Create or update a repository file</summary>

Writes content to a file path, creating or updating with optional SHA protection.

**Inputs:**

- `oauth_token` (object, required) — GitHub token payload
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `path` (string, required) — File path
- `content` (string, required) — File content
- `message` (string, required) — Commit message

**Output:**

```json
{
	"ok": true,
	"data": {"content": {"path": "README.md"}, "commit": {"sha": "abc123"}}
}
```

**Usage Example:**

```bash
POST /mcp/cl-github-mcp-server/create_or_update_file

{
	"oauth_token": {"token": "${GITHUB_TOKEN}", "scopes": ["repo"]},
	"owner": "octocat",
	"repo": "demo",
	"path": "README.md",
	"content": "# Demo",
	"message": "docs: add readme"
}
```

</details>

<details>
<summary><code>fork_repository</code> — Fork repository</summary>

Forks a repository into the authenticated user account or specified organization.

**Inputs:**

- `oauth_token` (object, required) — GitHub token payload
- `owner` (string, required) — Source owner
- `repo` (string, required) — Source repository
- `org` (string, optional) — Destination organization

**Output:**

```json
{
	"ok": true,
	"data": {"full_name": "my-user/repo", "fork": true}
}
```

**Usage Example:**

```bash
POST /mcp/cl-github-mcp-server/fork_repository

{
	"oauth_token": {"token": "${GITHUB_TOKEN}", "scopes": ["repo"]},
	"owner": "github",
	"repo": "docs"
}
```

</details>

<details>
<summary><code>create_branch</code> — Create branch</summary>

Creates a new branch from a specified SHA or the default branch head.

**Inputs:**

- `oauth_token` (object, required) — GitHub token payload
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `branch_name` (string, required) — New branch name
- `sha` (string, optional) — Base commit SHA

**Output:**

```json
{
	"ok": true,
	"data": {"ref": "refs/heads/feature/new-api", "object": {"sha": "abc123"}}
}
```

**Usage Example:**

```bash
POST /mcp/cl-github-mcp-server/create_branch

{
	"oauth_token": {"token": "${GITHUB_TOKEN}", "scopes": ["repo"]},
	"owner": "octocat",
	"repo": "demo",
	"branch_name": "feature/new-api"
}
```

</details>

<details>
<summary><code>push_files</code> — Push multiple files atomically</summary>

Commits multiple file changes in one tree/commit update operation.

**Inputs:**

- `oauth_token` (object, required) — GitHub token payload
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `files_json` (string, required) — JSON array of file path/content objects
- `message` (string, required) — Commit message
- `branch` (string, optional) — Target branch

**Output:**

```json
{
	"ok": true,
	"data": {"commit_sha": "abc123", "branch": "main", "message": "chore: update files"}
}
```

**Usage Example:**

```bash
POST /mcp/cl-github-mcp-server/push_files

{
	"oauth_token": {"token": "${GITHUB_TOKEN}", "scopes": ["repo"]},
	"owner": "octocat",
	"repo": "demo",
	"files_json": "[{\"path\":\"docs/a.md\",\"content\":\"A\"},{\"path\":\"docs/b.md\",\"content\":\"B\"}]",
	"message": "docs: add two files"
}
```

</details>

<details>
<summary><code>pull_request_read</code> — Read pull request details</summary>

Fetches PR data with method variants for files, status, comments, and review comments.

**Inputs:**

- `oauth_token` (object, required) — GitHub token payload
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `pull_number` (integer, required) — Pull request number
- `method` (string, optional) — `get`, `get_files`, `get_status`, `get_comments`, `get_review_comments`

**Output:**

```json
{
	"ok": true,
	"data": {"number": 7, "title": "feat: add API", "state": "open"}
}
```

**Usage Example:**

```bash
POST /mcp/cl-github-mcp-server/pull_request_read

{
	"oauth_token": {"token": "${GITHUB_TOKEN}", "scopes": ["repo"]},
	"owner": "octocat",
	"repo": "demo",
	"pull_number": 7,
	"method": "get_files"
}
```

</details>

<details>
<summary><code>list_pull_requests</code> — List pull requests</summary>

Lists pull requests with filter and sorting options.

**Inputs:**

- `oauth_token` (object, required) — GitHub token payload
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `state` (string, optional) — `open`, `closed`, `all`
- `sort` (string, optional) — `created`, `updated`, `popularity`, `long-running`
- `direction` (string, optional) — `asc` or `desc`

**Output:**

```json
{
	"ok": true,
	"data": {"pull_requests": [{"number": 7, "title": "feat: add API"}], "count": 1}
}
```

**Usage Example:**

```bash
POST /mcp/cl-github-mcp-server/list_pull_requests

{
	"oauth_token": {"token": "${GITHUB_TOKEN}", "scopes": ["repo"]},
	"owner": "octocat",
	"repo": "demo",
	"state": "open"
}
```

</details>

<details>
<summary><code>search_pull_requests</code> — Search pull requests</summary>

Searches pull requests using GitHub search syntax with optional repository scope.

**Inputs:**

- `oauth_token` (object, required) — GitHub token payload
- `query` (string, required) — Search query
- `sort` (string, optional) — Sort field
- `order` (string, optional) — `asc` or `desc`
- `owner` (string, optional) — Repository owner
- `repo` (string, optional) — Repository name

**Output:**

```json
{
	"ok": true,
	"data": {"items": [{"number": 7, "title": "feat: add API", "state": "open"}]}
}
```

**Usage Example:**

```bash
POST /mcp/cl-github-mcp-server/search_pull_requests

{
	"oauth_token": {"token": "${GITHUB_TOKEN}", "scopes": ["repo"]},
	"query": "is:pr is:open review:required",
	"owner": "octocat",
	"repo": "demo"
}
```

</details>

<details>
<summary><code>create_pull_request</code> — Create pull request</summary>

Creates a PR from head to base with optional draft mode and body.

**Inputs:**

- `oauth_token` (object, required) — GitHub token payload
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `title` (string, required) — PR title
- `head` (string, required) — Source branch
- `base` (string, required) — Target branch

**Output:**

```json
{
	"ok": true,
	"data": {"number": 8, "url": "https://github.com/owner/repo/pull/8", "state": "open"}
}
```

**Usage Example:**

```bash
POST /mcp/cl-github-mcp-server/create_pull_request

{
	"oauth_token": {"token": "${GITHUB_TOKEN}", "scopes": ["repo"]},
	"owner": "octocat",
	"repo": "demo",
	"title": "feat: add docs",
	"head": "feature/docs",
	"base": "main"
}
```

</details>

<details>
<summary><code>update_pull_request</code> — Update pull request</summary>

Updates PR title, body, state, base branch, draft state, and reviewer requests.

**Inputs:**

- `oauth_token` (object, required) — GitHub token payload
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `pull_number` (integer, required) — Pull request number
- `title` (string, optional) — Updated title
- `state` (string, optional) — `open` or `closed`

**Output:**

```json
{
	"ok": true,
	"data": {"number": 8, "state": "open", "title": "feat: add docs v2"}
}
```

**Usage Example:**

```bash
POST /mcp/cl-github-mcp-server/update_pull_request

{
	"oauth_token": {"token": "${GITHUB_TOKEN}", "scopes": ["repo"]},
	"owner": "octocat",
	"repo": "demo",
	"pull_number": 8,
	"title": "feat: add docs v2"
}
```

</details>

<details>
<summary><code>merge_pull_request</code> — Merge pull request</summary>

Merges a PR with merge, squash, or rebase strategy.

**Inputs:**

- `oauth_token` (object, required) — GitHub token payload
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `pull_number` (integer, required) — Pull request number
- `merge_method` (string, optional) — `merge`, `squash`, `rebase`

**Output:**

```json
{
	"ok": true,
	"data": {"merged": true, "sha": "abc123", "message": "Pull Request successfully merged"}
}
```

**Usage Example:**

```bash
POST /mcp/cl-github-mcp-server/merge_pull_request

{
	"oauth_token": {"token": "${GITHUB_TOKEN}", "scopes": ["repo"]},
	"owner": "octocat",
	"repo": "demo",
	"pull_number": 8,
	"merge_method": "squash"
}
```

</details>

<details>
<summary><code>update_pull_request_branch</code> — Update PR branch from base</summary>

Updates the PR branch with latest changes from the base branch.

**Inputs:**

- `oauth_token` (object, required) — GitHub token payload
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `pull_number` (integer, required) — Pull request number
- `expected_head_sha` (string, optional) — Concurrency guard SHA

**Output:**

```json
{
	"ok": true,
	"data": {"message": "Branch update requested"}
}
```

**Usage Example:**

```bash
POST /mcp/cl-github-mcp-server/update_pull_request_branch

{
	"oauth_token": {"token": "${GITHUB_TOKEN}", "scopes": ["repo"]},
	"owner": "octocat",
	"repo": "demo",
	"pull_number": 8
}
```

</details>

<details>
<summary><code>pull_request_review_write</code> — Write PR reviews and thread actions</summary>

Creates, submits, and deletes pending reviews, and resolves/unresolves review threads.

**Inputs:**

- `oauth_token` (object, required) — GitHub token payload
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `pull_number` (integer, required) — Pull request number
- `method` (string, required) — `create`, `submit_pending`, `delete_pending`, `resolve_thread`, `unresolve_thread`
- `event` (string, optional) — `APPROVE`, `REQUEST_CHANGES`, `COMMENT`

**Output:**

```json
{
	"ok": true,
	"data": {"status": "review_updated", "pull_number": 8}
}
```

**Usage Example:**

```bash
POST /mcp/cl-github-mcp-server/pull_request_review_write

{
	"oauth_token": {"token": "${GITHUB_TOKEN}", "scopes": ["repo"]},
	"owner": "octocat",
	"repo": "demo",
	"pull_number": 8,
	"method": "submit_pending",
	"event": "APPROVE",
	"body": "Looks good"
}
```

</details>

<details>
<summary><code>add_reply_to_pull_request_comment</code> — Reply to PR comment</summary>

Adds a reply to an existing pull request review comment thread.

**Inputs:**

- `oauth_token` (object, required) — GitHub token payload
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `pull_number` (integer, required) — Pull request number
- `comment_id` (integer, required) — Comment ID to reply to
- `body` (string, required) — Reply text

**Output:**

```json
{
	"ok": true,
	"data": {"id": 1001, "body": "Thanks for the note"}
}
```

**Usage Example:**

```bash
POST /mcp/cl-github-mcp-server/add_reply_to_pull_request_comment

{
	"oauth_token": {"token": "${GITHUB_TOKEN}", "scopes": ["repo"]},
	"owner": "octocat",
	"repo": "demo",
	"pull_number": 8,
	"comment_id": 100,
	"body": "Addressed in latest commit"
}
```

</details>

<details>
<summary><code>get_latest_release</code> — Get latest release</summary>

Returns the latest published release of a repository.

**Inputs:**

- `oauth_token` (object, required) — GitHub token payload
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name

**Output:**

```json
{
	"ok": true,
	"data": {"tag_name": "v2.3.0", "name": "Release 2.3.0", "draft": false}
}
```

**Usage Example:**

```bash
POST /mcp/cl-github-mcp-server/get_latest_release

{
	"oauth_token": {"token": "${GITHUB_TOKEN}", "scopes": ["repo"]},
	"owner": "github",
	"repo": "docs"
}
```

</details>

<details>
<summary><code>list_releases</code> — List releases</summary>

Lists repository releases with pagination.

**Inputs:**

- `oauth_token` (object, required) — GitHub token payload
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `page` (integer, optional) — Page number
- `per_page` (integer, optional) — Results per page

**Output:**

```json
{
	"ok": true,
	"data": {"releases": [{"tag_name": "v2.3.0", "name": "Release 2.3.0"}], "count": 1}
}
```

**Usage Example:**

```bash
POST /mcp/cl-github-mcp-server/list_releases

{
	"oauth_token": {"token": "${GITHUB_TOKEN}", "scopes": ["repo"]},
	"owner": "github",
	"repo": "docs",
	"page": 1,
	"per_page": 30
}
```

</details>

<details>
<summary><code>get_release_by_tag</code> — Get release by tag</summary>

Fetches one release by tag name.

**Inputs:**

- `oauth_token` (object, required) — GitHub token payload
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `tag` (string, required) — Tag name

**Output:**

```json
{
	"ok": true,
	"data": {"tag_name": "v2.3.0", "name": "Release 2.3.0", "url": "https://github.com/owner/repo/releases/tag/v2.3.0"}
}
```

**Usage Example:**

```bash
POST /mcp/cl-github-mcp-server/get_release_by_tag

{
	"oauth_token": {"token": "${GITHUB_TOKEN}", "scopes": ["repo"]},
	"owner": "github",
	"repo": "docs",
	"tag": "v2.3.0"
}
```

</details>

<details>
<summary><code>get_label</code> — Get repository label</summary>

Retrieves metadata for a specific repository label.

**Inputs:**

- `oauth_token` (object, required) — GitHub token payload
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `name` (string, required) — Label name

**Output:**

```json
{
	"ok": true,
	"data": {"name": "bug", "color": "d73a4a", "description": "Something is not working"}
}
```

**Usage Example:**

```bash
POST /mcp/cl-github-mcp-server/get_label

{
	"oauth_token": {"token": "${GITHUB_TOKEN}", "scopes": ["repo"]},
	"owner": "github",
	"repo": "docs",
	"name": "bug"
}
```

</details>

<details>
<summary><code>get_me</code> — Get authenticated user</summary>

Returns identity details for the token owner.

**Inputs:**

- `oauth_token` (object, required) — GitHub token payload

**Output:**

```json
{
	"ok": true,
	"data": {"login": "octocat", "id": 1, "html_url": "https://github.com/octocat"}
}
```

**Usage Example:**

```bash
POST /mcp/cl-github-mcp-server/get_me

{
	"oauth_token": {"token": "${GITHUB_TOKEN}", "scopes": []}
}
```

</details>

<details>
<summary><code>sub_issue_write</code> — Manage sub-issues</summary>

Adds, removes, or reprioritizes sub-issues for a parent issue.

**Inputs:**

- `oauth_token` (object, required) — GitHub token payload
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `issue_number` (integer, required) — Parent issue number
- `method` (string, required) — `add`, `remove`, `reprioritize`
- `sub_issue_id` (integer, required) — Sub-issue identifier

**Output:**

```json
{
	"ok": true,
	"data": {"status": "updated", "issue_number": 101}
}
```

**Usage Example:**

```bash
POST /mcp/cl-github-mcp-server/sub_issue_write

{
	"oauth_token": {"token": "${GITHUB_TOKEN}", "scopes": ["repo"]},
	"owner": "octocat",
	"repo": "demo",
	"issue_number": 101,
	"method": "add",
	"sub_issue_id": 202
}
```

</details>

<details>
<summary><code>assign_copilot_to_issue</code> — Assign Copilot coding agent</summary>

Assigns GitHub Copilot coding agent to work on an issue.

**Inputs:**

- `oauth_token` (object, required) — GitHub token payload
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `issue_number` (integer, required) — Issue number
- `base_ref` (string, optional) — Branch to start from
- `custom_instructions` (string, optional) — Extra agent instructions

**Output:**

```json
{
	"ok": true,
	"data": {"issue_number": 101, "status": "assigned", "pull_request_url": null}
}
```

**Usage Example:**

```bash
POST /mcp/cl-github-mcp-server/assign_copilot_to_issue

{
	"oauth_token": {"token": "${GITHUB_TOKEN}", "scopes": ["repo"]},
	"owner": "octocat",
	"repo": "demo",
	"issue_number": 101,
	"base_ref": "main"
}
```

</details>

<details>
<summary><code>request_copilot_review</code> — Request Copilot PR review</summary>

Requests an automated Copilot review on a pull request.

**Inputs:**

- `oauth_token` (object, required) — GitHub token payload
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `pull_number` (integer, required) — Pull request number

**Output:**

```json
{
	"ok": true,
	"data": {"pull_number": 8, "status": "review_requested"}
}
```

**Usage Example:**

```bash
POST /mcp/cl-github-mcp-server/request_copilot_review

{
	"oauth_token": {"token": "${GITHUB_TOKEN}", "scopes": ["repo"]},
	"owner": "octocat",
	"repo": "demo",
	"pull_number": 8
}
```

</details>

---

## API Parameters Reference

<details>
<summary><strong>Common Parameters</strong></summary>

- `oauth_token` — Structured token object with `token` and optional `scopes` list
- `owner` — GitHub repository owner or organization login
- `repo` — Repository name
- `page` / `perPage` / `per_page` — Pagination controls used by listing/search tools
- `method` — Operation selector for multiplexed tools (for example PR read/review operations)

</details>

<details>
<summary><strong>Resource Formats</strong></summary>

**Repository Resource:**

```
owner/repo
Example: github/docs
```

**Branch Reference:**

```
refs/heads/{branch_name}
Example: refs/heads/main
```

**Issue / Pull Request Number:**

```
integer identifier
Example: 101
```

**File Path Resource:**

```
/{path}
Example: /README.md
```

</details>

---

## Authentication Guide

<details>
<summary><strong>OAuth / API Key Setup</strong></summary>

All tools require GitHub authentication. You can use a GitHub personal access token, or generate OAuth tokens with the included helper script.

### Step 1: Create GitHub OAuth App

1. Go to [GitHub Developer Settings](https://github.com/settings/developers)
2. Open **OAuth Apps** and click **New OAuth App**
3. Set **Authorization callback URL** to `http://127.0.0.1:3000/callback`

### Step 2: Configure Credentials

1. Add credentials to environment variables:
2. `GITHUB_CLIENT_ID=...`
3. `GITHUB_CLIENT_SECRET=...`
4. Optional: `GITHUB_SCOPES=repo,read:org`

### Step 3: Authenticate

Run the OAuth helper script from project root:

```bash
python3 oauth_script.py
```

The script opens the browser, handles callback locally, exchanges the code, and prints token JSON.

Refer to [GitHub OAuth Docs](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authorizing-oauth-apps) for details.

### Step 4: Required Scopes

Ensure your token has these scopes:

- `repo` — Required by the repository, file, issue, PR, release, and Copilot tools
- `read:org` — Recommended for organization contributor discovery workflows
- `public_repo` — Optional for public-only issue/comment reads

</details>

---

## Troubleshooting

<details>
<summary><strong>Common Issues & Solutions</strong></summary>

### **Missing or Invalid Token**

- **Cause:** `oauth_token.token` missing or malformed
- **Solution:**
	1. Provide `oauth_token` as `{ "token": "...", "scopes": [...] }`
	2. Verify the token is active in GitHub settings
	3. Re-run OAuth flow or generate a new PAT

### **Missing Scope Error**

- **Cause:** Token does not include required scope (`repo` in most tools)
- **Solution:**
	1. Regenerate token with required scopes
	2. Pass the granted scopes list in `oauth_token.scopes`
	3. Retry the request and confirm `scope_check` in `meta`

### **Malformed Request Payload**

- **Cause:** Invalid JSON or wrong field names/types
- **Solution:**
	1. Validate JSON syntax
	2. Ensure required fields are provided
	3. Match parameter casing (for example `perPage` vs `per_page`) by tool schema

### **GitHub API Forbidden (403)**

- **Cause:** Scope restrictions, organization policy, or branch protection
- **Solution:**
	1. Check token scopes and org permissions
	2. Validate branch protection rules for write/merge operations
	3. Retry with sufficient repository permissions

### **OAuth Callback Timeout**

- **Cause:** OAuth browser approval not completed within timeout
- **Solution:**
	1. Ensure callback URL is exactly `http://127.0.0.1:3000/callback`
	2. Re-run `python3 oauth_script.py`
	3. Approve authorization promptly in browser

</details>

---

## Resources

<details>
<summary><strong>External Documentation</strong></summary>

- **[GitHub REST API Documentation](https://docs.github.com/en/rest)** — Official GitHub REST API reference
- **[GitHub OAuth Apps Guide](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authorizing-oauth-apps)** — OAuth setup and authorization flow
- **[FastMCP Docs](https://gofastmcp.com/v2/getting-started/welcome)** — FastMCP framework documentation

</details>

---
