**Comprehensive GitHub API access for repositories, issues, pull requests, and code — all through typed MCP tools.**

A Model Context Protocol (MCP) server that exposes GitHub's API for managing repositories, issues, pull requests, branches, releases, tags, branch protection, and repository rulesets.

> **v2.0.0:** Tool responses changed from a JSON-encoded string to native typed structured objects. The `data` field on each tool response is now a typed model (one per tool) instead of an untyped dict serialized into a raw string.


## Overview

The MewCP GitHub MCP Server provides:

- Repository management — get, create, update, and fork repositories; create or update files and push multi-file commits
- Search across GitHub — repositories, code, users, issues, and pull requests
- Issue tracking — list, get, create, comment on, and update issues, including sub-issue relationships and Copilot assignment
- Pull request workflows — read, list, create, update, merge PRs, manage branch updates, write reviews, reply to comments, and request Copilot review
- Repository administration — branches, commits, file contents, tags, releases, labels, branch protection, PR review protection, and repository rulesets

Perfect for:

- AI agents that need to read and act on GitHub repository state (issues, PRs, files, commits)
- Automating routine GitHub workflows — issue triage, PR review requests, release lookups
- Enforcing and auditing repository governance — branch protection, PR review requirements, rulesets


## Tools


<details>
<summary><code>get_repo</code> — Get basic details for a GitHub repository.</summary>

Get basic details for a GitHub repository.

**Inputs:**
```
- `owner` (string, required) — Repository owner, for example octocat
- `repo` (string, required) — Repository name
```

**Output `data` schema:**

```typescript
{
  id: number | null;
  name: string | null;
  full_name: string | null;
  owner: object | null;
  html_url: string | null;
  description: string | null;
  private: boolean | null;
  fork: boolean | null;
  url: string | null;
  default_branch: string | null;
  created_at: string | null;
  updated_at: string | null;
  stargazers_count: number | null;
  language: string | null;
  has_issues: boolean | null;
  has_downloads: boolean | null;
  forks_count: number | null;
}
```

</details>


<details>
<summary><code>update_repository</code> — Updates repository metadata or renames a repository.</summary>

Updates repository metadata or renames a repository. Only the fields you provide are changed — others keep their current value. NOTE: this overwrites the current field values — the original state is not stored after the call. The response includes both the before and after state so you have a full record of what changed.

**Inputs:**
```
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `name` (string, optional) — New repository name (to rename)
- `description` (string, optional) — Repository description
- `private` (boolean, optional) — Make repository private/public
- `default_branch` (string, optional) — Default branch name
```

**Output `data` schema:**

```typescript
{
  before: {
    id: number | null;
    name: string | null;
    full_name: string | null;
    owner: object | null;
    html_url: string | null;
    description: string | null;
    private: boolean | null;
    fork: boolean | null;
    url: string | null;
    default_branch: string | null;
    created_at: string | null;
    updated_at: string | null;
    stargazers_count: number | null;
    language: string | null;
    has_issues: boolean | null;
    has_downloads: boolean | null;
    forks_count: number | null;
  };
  after: {
    id: number | null;
    name: string | null;
    full_name: string | null;
    html_url: string | null;
    private: boolean | null;
    description: string | null;
    default_branch: string | null;
  };
}
```

</details>


<details>
<summary><code>create_repository</code> — Create a new GitHub repository in your personal account or an organization.</summary>

Create a new GitHub repository in your personal account or an organization.

**Inputs:**
```
- `name` (string, required) — Repository name (required). Must be unique in account/organization.
- `description` (string, optional) — Repository description (optional).
- `private` (boolean, optional, default: false) — Make repository private (default: False for public).
- `auto_init` (boolean, optional, default: false) — Auto-initialize with README (default: False).
- `gitignore_template` (string, optional) — Gitignore template name. Example: 'Python', 'Node'.
- `org` (string, optional) — Organization name to create repo in (optional).
```

**Output `data` schema:**

```typescript
{
  id: number | null;
  name: string | null;
  full_name: string | null;
  url: string | null;
  html_url: string | null;
  owner: object | null;
  private: boolean | null;
  created_at: string | null;
}
```

</details>


<details>
<summary><code>fork_repository</code> — Fork a repository to your personal account or an organization.</summary>

Fork a repository to your personal account or an organization.

**Inputs:**
```
- `owner` (string, required) — Original repository owner.
- `repo` (string, required) — Original repository name.
- `org` (string, optional) — Organization name to fork into (optional).
```

**Output `data` schema:**

```typescript
{
  id: number | null;
  name: string | null;
  full_name: string | null;
  url: string | null;
  html_url: string | null;
  owner: object | null;
  fork: boolean | null;
}
```

</details>


<details>
<summary><code>create_or_update_file</code> — Create or update a file in a repository. Prevents accidental overwrites with SHA validation.</summary>

Create or update a file in a repository. Prevents accidental overwrites with SHA validation.

**Inputs:**
```
- `owner` (string, required) — Repository owner name.
- `repo` (string, required) — Repository name.
- `path` (string, required) — File path in repository. Example: 'src/main.py'.
- `content` (string, required) — File content to write.
- `message` (string, required) — Commit message.
- `branch` (string, optional) — Target branch name (optional).
- `sha` (string, optional) — File SHA for updates (optional).
```

**Output `data` schema:**

```typescript
{
  content: object | null;
  commit: object | null;
}
```

</details>


<details>
<summary><code>push_files</code> — Push multiple files to a repository in a single atomic commit.</summary>

Push multiple files to a repository in a single atomic commit.

**Inputs:**
```
- `owner` (string, required) — Repository owner name.
- `repo` (string, required) — Repository name.
- `files_json` (string, required) — JSON array of file objects with path and content keys. Example: '[{"path": "file1.txt", "content": "hello"}]'
- `message` (string, required) — Commit message.
- `branch` (string, optional) — Target branch name (optional).
- `author_name` (string, optional) — Author name (optional).
- `author_email` (string, optional) — Author email (optional).
```

**Output `data` schema:**

```typescript
{
  commit_sha: string | null;
  tree_sha: string | null;
  branch: string | null;
  message: string | null;
  url: string | null;
}
```

</details>


<details>
<summary><code>search_repositories</code> — Search GitHub repositories.</summary>

Search GitHub repositories.

**Inputs:**
```
- `query` (string, required) — Search query
- `sort` (string, optional, default: "stars") — Sort by: stars, forks, updated
- `order` (string, optional, default: "desc") — Order: asc or desc
- `page` (integer, optional, default: 1) — Page number
- `perPage` (integer, optional, default: 30) — Items per page
```

**Output `data` schema:**

```typescript
{
  items: {
    id: number | null;
    name: string | null;
    full_name: string | null;
    private: boolean | null;
    html_url: string | null;
    description: string | null;
    stars: number | null;
  }[];
  total_count: number;
}
```

</details>


<details>
<summary><code>search_code</code> — Fast and precise code search across GitHub repositories.</summary>

Fast and precise code search across GitHub repositories.

**Inputs:**
```
- `query` (string, required) — Search query using GitHub code search syntax.
- `sort` (string, optional, default: "indexed") — Sort field. Only 'indexed' is supported.
- `order` (string, optional, default: "desc") — Sort order: asc or desc.
- `page` (integer, optional, default: 1) — Page number.
- `perPage` (integer, optional, default: 30) — Results per page (1-100).
```

**Output `data` schema:**

```typescript
{
  total_count: number;
  incomplete_results: boolean;
  items: {
    name: string | null;
    path: string | null;
    repository: string | null;
    url: string | null;
  }[];
}
```

</details>


<details>
<summary><code>search_users</code> — Search GitHub users by name, location, followers, or other attributes.</summary>

Search GitHub users by name, location, followers, or other attributes.

**Inputs:**
```
- `query` (string, required) — User search query using GitHub's search syntax.
- `sort` (string, optional, default: "followers") — Sort field: followers, repositories, joined.
- `order` (string, optional, default: "desc") — Sort order: asc or desc.
- `page` (integer, optional, default: 1) — Page number.
- `perPage` (integer, optional, default: 30) — Results per page (1-100).
```

**Output `data` schema:**

```typescript
{
  total_count: number;
  incomplete_results: boolean;
  items: {
    login: string | null;
    id: number | null;
    profile_url: string | null;
    avatar_url: string | null;
  }[];
}
```

</details>


<details>
<summary><code>search_issues</code> — Search issues and pull requests across GitHub.</summary>

Search issues and pull requests across GitHub.

**Inputs:**
```
- `query` (string, required) — Search query using GitHub issue search syntax.
- `sort` (string, optional, default: "updated") — Sort field: updated, created, comments.
- `order` (string, optional, default: "desc") — Sort order: asc or desc.
- `owner` (string, optional) — Repository owner (optional).
- `repo` (string, optional) — Repository name (optional).
- `page` (integer, optional, default: 1) — Page number.
- `perPage` (integer, optional, default: 30) — Results per page (1-100).
```

**Output `data` schema:**

```typescript
{
  total_count: number;
  incomplete_results: boolean;
  items: {
    number: number | null;
    title: string | null;
    state: string | null;
    body: string | null;
    url: string | null;
    comments: number | null;
    user: string | null;
  }[];
}
```

</details>


<details>
<summary><code>search_pull_requests</code> — Search for pull requests across GitHub using search syntax.</summary>

Search for pull requests across GitHub using search syntax.

**Inputs:**
```
- `query` (string, required) — Search query using GitHub search syntax.
- `sort` (string, optional, default: "updated") — Sort field: updated, created, comments.
- `order` (string, optional, default: "desc") — Sort order: asc or desc.
- `owner` (string, optional) — Repository owner (optional).
- `repo` (string, optional) — Repository name (optional).
- `page` (integer, optional, default: 1) — Page number.
- `per_page` (integer, optional, default: 30) — Results per page.
```

**Output `data` schema:**

```typescript
{
  total_count: number;
  incomplete_results: boolean;
  pull_requests: {
    number: number | null;
    title: string | null;
    state: string | null;
    url: string | null;
    user: string | null;
    created_at: string | null;
    updated_at: string | null;
    comments: number | null;
  }[];
  page: number | null;
  per_page: number | null;
}
```

</details>


<details>
<summary><code>list_issues</code> — List issues in a GitHub repository.</summary>

List issues in a GitHub repository.

**Inputs:**
```
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `state` (string, optional, default: "open") — Filter by state: open, closed, all
- `labels` (string, optional) — Comma-separated label names to filter by
- `page` (integer, optional, default: 1) — Page number
- `perPage` (integer, optional, default: 30) — Items per page
```

**Output `data` schema:**

```typescript
{
  issues: {
    number: number | null;
    title: string | null;
    state: string | null;
    url: string | null;
    body: string | null;
    user: string | null;
    labels: string[];
    created_at: string | null;
    updated_at: string | null;
  }[];
  count: number;
}
```

</details>


<details>
<summary><code>get_issue</code> — Get detailed information about a specific GitHub issue.</summary>

Get detailed information about a specific GitHub issue.

**Inputs:**
```
- `owner` (string, required) — Repository owner name.
- `repo` (string, required) — Repository name.
- `issue_number` (integer, required) — Issue number.
```

**Output `data` schema:**

```typescript
{
  number: number | null;
  title: string | null;
  body: string | null;
  state: string | null;
  state_reason: string | null;
  labels: string[];
  assignees: string[];
  url: string | null;
  user: string | null;
  created_at: string | null;
  updated_at: string | null;
  closed_at: string | null;
}
```

</details>


<details>
<summary><code>get_issue_comments</code> — Get all comments on a GitHub issue with pagination support.</summary>

Get all comments on a GitHub issue with pagination support.

**Inputs:**
```
- `owner` (string, required) — Repository owner name.
- `repo` (string, required) — Repository name.
- `issue_number` (integer, required) — Issue number.
- `page` (integer, optional, default: 1) — Page number.
- `perPage` (integer, optional, default: 30) — Comments per page (1-100).
```

**Output `data` schema:**

```typescript
{
  comments: {
    id: number | null;
    body: string | null;
    url: string | null;
    user: string | null;
    created_at: string | null;
    updated_at: string | null;
  }[];
  page: number | null;
  per_page: number | null;
}
```

</details>


<details>
<summary><code>create_issue</code> — Create a new GitHub issue in a repository.</summary>

Create a new GitHub issue in a repository.

**Inputs:**
```
- `owner` (string, required) — Repository owner name.
- `repo` (string, required) — Repository name.
- `title` (string, required) — Issue title (required).
- `body` (string, optional) — Issue description (optional).
- `assignees` (string[], optional) — List of usernames to assign (optional).
- `labels` (string[], optional) — List of label names (optional).
- `milestone` (integer, optional) — Milestone ID (optional).
```

**Output `data` schema:**

```typescript
{
  id: number | null;
  number: number | null;
  url: string | null;
  title: string | null;
}
```

</details>


<details>
<summary><code>add_issue_comment</code> — Add a comment to a GitHub issue or pull request.</summary>

Add a comment to a GitHub issue or pull request.

**Inputs:**
```
- `owner` (string, required) — Repository owner name.
- `repo` (string, required) — Repository name.
- `issue_number` (integer, required) — Issue or pull request number.
- `body` (string, required) — Comment text (required).
```

**Output `data` schema:**

```typescript
{
  id: number | null;
  url: string | null;
  body: string | null;
  user: string | null;
}
```

</details>


<details>
<summary><code>update_issue</code> — Updates a GitHub issue's title, body, state, assignees, labels, or milestone.</summary>

Updates a GitHub issue's title, body, state, assignees, labels, or milestone. Only the fields you provide are changed — others keep their current value. NOTE: this overwrites the current field values — the original state is not stored after the call. The response includes both the before and after state so you have a full record of what changed.

**Inputs:**
```
- `owner` (string, required) — Repository owner name.
- `repo` (string, required) — Repository name.
- `issue_number` (integer, required) — Issue number to update.
- `title` (string, optional) — New issue title (optional).
- `body` (string, optional) — New issue description (optional).
- `state` (string, optional) — New state: open or closed (optional).
- `state_reason` (string, optional) — Reason when closing: completed, not_planned (optional).
- `assignees` (string[], optional) — New list of assignees (optional).
- `labels` (string[], optional) — New list of labels (optional).
- `milestone` (integer, optional) — Milestone ID (optional).
```

**Output `data` schema:**

```typescript
{
  before: {
    number: number | null;
    title: string | null;
    body: string | null;
    state: string | null;
    state_reason: string | null;
    labels: string[];
    assignees: string[];
    url: string | null;
    user: string | null;
    created_at: string | null;
    updated_at: string | null;
    closed_at: string | null;
  };
  after: {
    id: number | null;
    number: number | null;
    url: string | null;
    title: string | null;
    state: string | null;
  };
}
```

</details>


<details>
<summary><code>list_org_repositories_by_contributor</code> — Find all repositories in an organization where specific contributors have made contributions.</summary>

Find all repositories in an organization where specific contributors have made contributions.

**Inputs:**
```
- `org` (string, required) — Organization name
- `contributor_usernames` (string, required) — GitHub username(s) to filter by. Comma-separated for multiple.
- `repo_type` (string, optional, default: "all") — Filter by type: all, public, or private.
```

**Output `data` schema:**

```typescript
{
  filter_contributors: string[];
  organization: string | null;
  repo_type_filter: string | null;
  total_repos_with_filtered_contributors: number;
  repos: {
    repo: string | null;
    full_name: string | null;
    url: string | null;
    private: boolean | null;
    description: string | null;
    contributors: {
      username: string | null;
      contributions: number;
    }[];
    total_filtered_contributions: number;
  }[];
}
```

</details>


<details>
<summary><code>sub_issue_write</code> — Manage sub-issues for a parent issue (add, remove, reprioritize).</summary>

Manage sub-issues for a parent issue (add, remove, reprioritize).

**Inputs:**
```
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `issue_number` (integer, required) — Parent issue number
- `method` (string, required) — Operation: add, remove, or reprioritize
- `sub_issue_id` (integer, required) — ID of the sub-issue
- `replace_parent` (boolean, optional, default: false) — Replace current parent when adding
- `after_id` (integer, optional) — Sub-issue ID to position after
- `before_id` (integer, optional) — Sub-issue ID to position before
```

**Output `data` schema:**

```typescript
{
  method: string | null;
  sub_issue_id: number | null;
  success: boolean | null;
  message: string | null;
}
```

</details>


<details>
<summary><code>assign_copilot_to_issue</code> — Assign GitHub Copilot to work on an issue.</summary>

Assign GitHub Copilot to work on an issue.

**Inputs:**
```
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `issue_number` (integer, required) — Issue number
- `base_ref` (string, optional) — Git reference to start from (optional).
- `custom_instructions` (string, optional) — Additional context for Copilot (optional).
```

**Output `data` schema:**

```typescript
{
  issue_number: number | null;
  assigned: boolean | null;
  job_id: number | null;
  status: string | null;
  pull_request_url: string | null;
}
```

</details>


<details>
<summary><code>pull_request_read</code> — Get details for a pull request with flexible method options (get, get_files, get_status, get_comments, get_review_comments).</summary>

Get details for a pull request with flexible method options (get, get_files, get_status, get_comments, get_review_comments).

**Inputs:**
```
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `pull_number` (integer, required) — Pull request number
- `method` (string, optional, default: "get") — Which PR data to retrieve: get, get_files, get_status, get_comments, get_review_comments
- `page` (integer, optional, default: 1) — Page number
- `per_page` (integer, optional, default: 30) — Results per page
```

**Output `data` schema:**

Polymorphic shape covering all 5 `method` variants. Only the fields relevant to the method used are populated; the rest stay `null`.

```typescript
{
  // method="get"
  number: number | null;
  title: string | null;
  body: string | null;
  state: string | null;
  state_reason: string | null;
  url: string | null;
  user: string | null;
  created_at: string | null;
  updated_at: string | null;
  merged_at: string | null;
  merged: boolean | null;
  merge_commit_sha: string | null;
  head: object | null;
  base: object | null;
  draft: boolean | null;
  additions: number | null;
  deletions: number | null;
  changed_files: number | null;
  commits: number | null;
  labels: string[] | null;
  assignees: string[] | null;
  reviewers: string[] | null;

  // method="get_files"
  files: object[] | null;
  total_files: number | null;

  // method="get_status"
  sha: string | null;
  total_count: number | null;
  statuses: object[] | null;

  // method="get_comments"
  comments: object[] | null;
  total_comments: number | null;

  // method="get_review_comments"
  review_comments: object[] | null;
  total_review_comments: number | null;

  // pagination (get_files / get_comments / get_review_comments)
  page: number | null;
  per_page: number | null;
}
```

</details>


<details>
<summary><code>list_pull_requests</code> — List pull requests in a GitHub repository with filtering and sorting options.</summary>

List pull requests in a GitHub repository with filtering and sorting options.

**Inputs:**
```
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `state` (string, optional, default: "open") — Filter by state: open, closed, or all
- `sort` (string, optional, default: "created") — Sort by: created, updated, popularity, or long-running
- `direction` (string, optional, default: "desc") — Sort direction: asc or desc
- `base` (string, optional) — Filter by base branch
- `head` (string, optional) — Filter by head branch (user:branch format)
- `page` (integer, optional, default: 1) — Page number
- `per_page` (integer, optional, default: 30) — Results per page
```

**Output `data` schema:**

```typescript
{
  pull_requests: {
    number: number | null;
    title: string | null;
    state: string | null;
    url: string | null;
    user: string | null;
    created_at: string | null;
    updated_at: string | null;
    draft: boolean | null;
    additions: number | null;
    deletions: number | null;
    changed_files: number | null;
  }[];
  total_count: number;
  page: number | null;
  per_page: number | null;
}
```

</details>


<details>
<summary><code>create_pull_request</code> — Create a new pull request in a GitHub repository.</summary>

Create a new pull request in a GitHub repository.

**Inputs:**
```
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `title` (string, required) — Pull request title
- `head` (string, required) — Branch containing changes
- `base` (string, required) — Branch to merge into
- `body` (string, optional) — PR description (optional)
- `draft` (boolean, optional, default: false) — Create as draft PR
- `maintainer_can_modify` (boolean, optional, default: true) — Allow maintainer edits
```

**Output `data` schema:**

```typescript
{
  number: number | null;
  title: string | null;
  state: string | null;
  draft: boolean | null;
  url: string | null;
  head_branch: string | null;
  base_branch: string | null;
  created_at: string | null;
  user: string | null;
}
```

</details>


<details>
<summary><code>update_pull_request</code> — Updates a pull request's title, body, state, base branch, draft status, maintainer-edit permission, or requested reviewers.</summary>

Updates a pull request's title, body, state, base branch, draft status, maintainer-edit permission, or requested reviewers. Only the fields you provide are changed — others keep their current value. NOTE: this overwrites the current field values — the original state is not stored after the call. The response includes both the before and after state so you have a full record of what changed.

**Inputs:**
```
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `pull_number` (integer, required) — Pull request number
- `title` (string, optional) — New title (optional)
- `body` (string, optional) — New description (optional)
- `state` (string, optional) — 'open' or 'closed' (optional)
- `base` (string, optional) — New base branch (optional)
- `draft` (boolean, optional) — Mark as draft/ready (optional)
- `maintainer_can_modify` (boolean, optional) — Allow maintainer edits (optional)
- `reviewers` (string[], optional) — Request reviews from users (optional)
```

**Output `data` schema:**

```typescript
{
  before: {
    number: number | null;
    title: string | null;
    body: string | null;
    state: string | null;
    state_reason: string | null;
    url: string | null;
    user: string | null;
    created_at: string | null;
    updated_at: string | null;
    merged_at: string | null;
    merged: boolean | null;
    merge_commit_sha: string | null;
    head: object | null;
    base: object | null;
    draft: boolean | null;
    additions: number | null;
    deletions: number | null;
    changed_files: number | null;
    commits: number | null;
    labels: string[] | null;
    assignees: string[] | null;
    reviewers: string[] | null;
    files: object[] | null;
    total_files: number | null;
    sha: string | null;
    total_count: number | null;
    statuses: object[] | null;
    comments: object[] | null;
    total_comments: number | null;
    review_comments: object[] | null;
    total_review_comments: number | null;
    page: number | null;
    per_page: number | null;
  };
  after: {
    number: number | null;
    title: string | null;
    state: string | null;
    draft: boolean | null;
    url: string | null;
    updated_at: string | null;
  };
}
```

</details>


<details>
<summary><code>merge_pull_request</code> — Merges a pull request using the given merge method (merge, squash, or rebase).</summary>

Merges a pull request using the given merge method (merge, squash, or rebase). This action is irreversible — once merged, the pull request cannot be un-merged; undoing it requires a new commit or pull request.

**Inputs:**
```
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `pull_number` (integer, required) — Pull request number
- `merge_method` (string, optional, default: "merge") — 'merge', 'squash', or 'rebase'
- `commit_title` (string, optional) — Custom commit title (optional)
- `commit_message` (string, optional) — Commit message details (optional)
```

**Output `data` schema:**

```typescript
{
  merged: boolean | null;
  sha: string | null;
  message: string | null;
}
```

</details>


<details>
<summary><code>update_pull_request_branch</code> — Update pull request branch with latest changes from base branch.</summary>

Update pull request branch with latest changes from base branch.

**Inputs:**
```
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `pull_number` (integer, required) — Pull request number
- `expected_head_sha` (string, optional) — Expected HEAD SHA (optional)
```

**Output `data` schema:**

```typescript
{
  message: string | null;
  url: string | null;
}
```

</details>


<details>
<summary><code>pull_request_review_write</code> — Write operations on PR reviews: create a review, submit a pending review, delete a pending review, or resolve/unresolve a review thread.</summary>

Write operations on PR reviews: create a review, submit a pending review, delete a pending review, or resolve/unresolve a review thread. Select the operation via `method`. NOTE: `delete_pending` permanently discards an unsubmitted draft review and any draft comments on it — this cannot be undone.

**Inputs:**
```
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `pull_number` (integer, required) — Pull request number
- `method` (string, required) — create, submit_pending, delete_pending, resolve_thread, or unresolve_thread
- `commit_id` (string, optional) — Commit SHA (required for create)
- `body` (string, optional) — Review comment text (optional)
- `event` (string, optional) — APPROVE, REQUEST_CHANGES, or COMMENT
- `thread_id` (string, optional) — Thread ID for thread operations
```

**Output `data` schema:**

Polymorphic shape covering all `method` variants (create / submit_pending / delete_pending / resolve_thread / unresolve_thread).

```typescript
{
  // method="create"
  id: number | null;
  node_id: string | null;
  state: string | null;
  body: string | null;
  user: string | null;
  submitted_at: string | null;

  // method="delete_pending"
  deleted: boolean | null;
  review_id: number | null;

  // method="resolve_thread" / "unresolve_thread"
  thread_id: string | null;
  resolved: boolean | null;
  message: string | null;
}
```

</details>


<details>
<summary><code>add_reply_to_pull_request_comment</code> — Add a reply to an existing PR comment.</summary>

Add a reply to an existing PR comment.

**Inputs:**
```
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `pull_number` (integer, required) — Pull request number
- `comment_id` (integer, required) — ID of the comment to reply to
- `body` (string, required) — Reply text
```

**Output `data` schema:**

```typescript
{
  id: number | null;
  user: string | null;
  body: string | null;
  created_at: string | null;
  url: string | null;
  in_reply_to_id: number | null;
}
```

</details>


<details>
<summary><code>request_copilot_review</code> — Request a code review from GitHub Copilot on a pull request.</summary>

Request a code review from GitHub Copilot on a pull request.

**Inputs:**
```
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `pull_number` (integer, required) — Pull request number
```

**Output `data` schema:**

```typescript
{
  pull_number: number | null;
  requested: boolean | null;
  reviewer: string | null;
  status: string | null;
}
```

</details>


<details>
<summary><code>list_branches</code> — List branches in a GitHub repository.</summary>

List branches in a GitHub repository.

**Inputs:**
```
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `page` (integer, optional, default: 1) — Page number
- `perPage` (integer, optional, default: 30) — Items per page
```

**Output `data` schema:**

```typescript
{
  branches: {
    name: string | null;
    sha: string | null;
    protected: boolean;
  }[];
}
```

</details>


<details>
<summary><code>list_commits</code> — List commits in a GitHub repository.</summary>

List commits in a GitHub repository.

**Inputs:**
```
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `sha` (string, optional) — Branch or commit SHA
- `path` (string, optional) — Filter commits by path
- `author` (string, optional) — Filter by author login
- `since` (string, optional) — ISO 8601 date: YYYY-MM-DD
- `until` (string, optional) — ISO 8601 date: YYYY-MM-DD
- `page` (integer, optional, default: 1) — Page number
- `perPage` (integer, optional, default: 30) — Items per page
```

**Output `data` schema:**

```typescript
{
  commits: {
    sha: string | null;
    message: string | null;
    author: object | null;
    committer: object | null;
    date: string | null;
  }[];
}
```

</details>


<details>
<summary><code>get_commit</code> — Get details of a specific commit.</summary>

Get details of a specific commit.

**Inputs:**
```
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `sha` (string, required) — Commit SHA
- `include_diff` (boolean, optional, default: true) — Include file changes in diff
```

**Output `data` schema:**

```typescript
{
  sha: string | null;
  message: string | null;
  author: object | null;
  committer: object | null;
  date: string | null;
  url: string | null;
  files: object[] | null;
}
```

</details>


<details>
<summary><code>get_file_contents</code> — Get file or directory contents from a GitHub repository.</summary>

Get file or directory contents from a GitHub repository.

**Inputs:**
```
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `path` (string, optional, default: "/") — File or directory path
- `ref` (string, optional) — Branch, tag, or commit SHA
```

**Output `data` schema:**

Polymorphic shape covering both directory and single-file responses.

```typescript
{
  type: string | null;

  // directory listing
  items: object[] | null;

  // single file
  name: string | null;
  path: string | null;
  size: number | null;
  url: string | null;
  content: string | null;
  encoding: string | null;
}
```

</details>


<details>
<summary><code>list_tags</code> — List all git tags in a repository with pagination support.</summary>

List all git tags in a repository with pagination support.

**Inputs:**
```
- `owner` (string, required) — Repository owner name.
- `repo` (string, required) — Repository name.
- `page` (integer, optional, default: 1) — Page number.
- `perPage` (integer, optional, default: 30) — Number of tags per page (1-100).
```

**Output `data` schema:**

```typescript
{
  tags: {
    name: string | null;
    commit: object | null;
    zipball_url: string | null;
    tarball_url: string | null;
  }[];
  page: number | null;
  per_page: number | null;
}
```

</details>


<details>
<summary><code>get_tag</code> — Get detailed information about a specific git tag.</summary>

Get detailed information about a specific git tag.

**Inputs:**
```
- `owner` (string, required) — Repository owner name.
- `repo` (string, required) — Repository name.
- `tag` (string, required) — Tag name to retrieve.
```

**Output `data` schema:**

```typescript
{
  ref: string | null;
  node_id: string | null;
  url: string | null;
  object: object | null;
}
```

</details>


<details>
<summary><code>get_latest_release</code> — Get the latest release in a repository.</summary>

Get the latest release in a repository.

**Inputs:**
```
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
```

**Output `data` schema:**

```typescript
{
  id: number | null;
  tag_name: string | null;
  name: string | null;
  draft: boolean | null;
  prerelease: boolean | null;
  created_at: string | null;
  published_at: string | null;
  url: string | null;
  body: string | null;
  author: string | null;
}
```

</details>


<details>
<summary><code>list_releases</code> — List releases in a repository.</summary>

List releases in a repository.

**Inputs:**
```
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `page` (integer, optional, default: 1) — Page number
- `per_page` (integer, optional, default: 30) — Results per page
```

**Output `data` schema:**

```typescript
{
  releases: {
    id: number | null;
    tag_name: string | null;
    name: string | null;
    draft: boolean | null;
    prerelease: boolean | null;
    created_at: string | null;
    published_at: string | null;
    url: string | null;
    author: string | null;
  }[];
  total_count: number;
  page: number | null;
  per_page: number | null;
}
```

</details>


<details>
<summary><code>get_release_by_tag</code> — Get a specific release by tag name.</summary>

Get a specific release by tag name.

**Inputs:**
```
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `tag` (string, required) — Tag name (e.g., 'v1.0.0')
```

**Output `data` schema:**

Response shape is identical to `get_latest_release`'s output.

```typescript
{
  id: number | null;
  tag_name: string | null;
  name: string | null;
  draft: boolean | null;
  prerelease: boolean | null;
  created_at: string | null;
  published_at: string | null;
  url: string | null;
  body: string | null;
  author: string | null;
}
```

</details>


<details>
<summary><code>get_label</code> — Get a specific label from a repository.</summary>

Get a specific label from a repository.

**Inputs:**
```
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `name` (string, required) — Label name
```

**Output `data` schema:**

```typescript
{
  id: number | null;
  name: string | null;
  color: string | null;
  description: string | null;
  url: string | null;
}
```

</details>


<details>
<summary><code>get_me</code> — Get details of the authenticated GitHub user.</summary>

Get details of the authenticated GitHub user.

**Inputs:**

_This tool takes no parameters._

**Output `data` schema:**

```typescript
{
  id: number | null;
  login: string | null;
  name: string | null;
  email: string | null;
  bio: string | null;
  company: string | null;
  location: string | null;
  public_repos: number;
  followers: number;
  following: number;
  created_at: string | null;
  updated_at: string | null;
  avatar_url: string | null;
  profile_url: string | null;
}
```

</details>


<details>
<summary><code>get_branch_protection</code> — Get branch protection rules for a specific branch.</summary>

Get branch protection rules for a specific branch.

**Inputs:**
```
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `branch` (string, required) — Branch name
```

**Output `data` schema:**

```typescript
{
  url: string | null;
  required_status_checks: object | null;
  enforce_admins: boolean | null;
  required_pull_request_reviews: object | null;
  restrictions: object | null;
  required_linear_history: boolean | null;
  allow_force_pushes: boolean | null;
  allow_deletions: boolean | null;
  block_creations: boolean | null;
  required_conversation_resolution: boolean | null;
  required_signatures: boolean | null;
  lock_branch: boolean | null;
  allow_fork_syncing: boolean | null;
}
```

</details>


<details>
<summary><code>set_branch_protection</code> — Set (create or replace) branch protection rules for a branch.</summary>

Set (create or replace) branch protection rules for a branch.

**Inputs:**
```
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `branch` (string, required) — Branch name
- `enforce_admins` (boolean, required) — Enforce for admins
- `required_status_checks` (object, optional) — Required status checks config
- `required_pull_request_reviews` (object, optional) — Required PR reviews config
- `restrictions` (object, optional) — User/team restrictions
- `required_linear_history` (boolean, optional, default: false) — Require linear history
- `allow_force_pushes` (boolean, optional) — Allow force pushes
- `allow_deletions` (boolean, optional, default: false) — Allow deletions
- `block_creations` (boolean, optional, default: false) — Block creations
- `required_conversation_resolution` (boolean, optional, default: false) — Require conversation resolution
- `lock_branch` (boolean, optional, default: false) — Lock branch
- `allow_fork_syncing` (boolean, optional, default: false) — Allow fork syncing
```

**Output `data` schema:**

```typescript
{
  url: string | null;
  branch: string | null;
  enforce_admins: boolean | null;
  required_linear_history: boolean | null;
  allow_force_pushes: boolean | null;
  allow_deletions: boolean | null;
  required_conversation_resolution: boolean | null;
  lock_branch: boolean | null;
}
```

</details>


<details>
<summary><code>delete_branch_protection</code> — DESTRUCTIVE — REQUIRES EXPLICIT USER CONFIRMATION BEFORE CALLING.</summary>

DESTRUCTIVE — REQUIRES EXPLICIT USER CONFIRMATION BEFORE CALLING. Permanently deletes all branch protection rules for the given branch. This action is irreversible — the branch protection configuration (required status checks, required reviews, restrictions, and all other settings) cannot be recovered once deleted. NEVER call this tool autonomously or as part of an automated flow. You MUST stop, tell the user exactly what will be deleted and that it is permanent, and wait for their explicit written confirmation before proceeding.

**Inputs:**
```
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `branch` (string, required) — Branch name
```

**Output `data` schema:**

```typescript
{
  deleted: boolean | null;
  branch: string | null;
}
```

</details>


<details>
<summary><code>get_pull_request_review_protection</code> — Get PR review requirements for a protected branch.</summary>

Get PR review requirements for a protected branch.

**Inputs:**
```
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `branch` (string, required) — Branch name
```

**Output `data` schema:**

```typescript
{
  url: string | null;
  dismiss_stale_reviews: boolean | null;
  require_code_owner_reviews: boolean | null;
  required_approving_review_count: number | null;
  require_last_push_approval: boolean | null;
  dismissal_restrictions: object | null;
}
```

</details>


<details>
<summary><code>update_pull_request_review_protection</code> — Updates the pull request review requirements for a protected branch.</summary>

Updates the pull request review requirements for a protected branch. Only the fields you provide are changed — others keep their current value. NOTE: this overwrites the current field values — the original state is not stored after the call. The response includes both the before and after state so you have a full record of what changed.

**Inputs:**
```
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `branch` (string, required) — Branch name
- `dismiss_stale_reviews` (boolean, optional) — Dismiss stale reviews
- `require_code_owner_reviews` (boolean, optional) — Require code owner reviews
- `required_approving_review_count` (integer, optional) — Required approving reviews
- `require_last_push_approval` (boolean, optional) — Require last push approval
- `dismissal_restrictions` (object, optional) — Dismissal restrictions
```

**Output `data` schema:**

```typescript
{
  before: {
    url: string | null;
    dismiss_stale_reviews: boolean | null;
    require_code_owner_reviews: boolean | null;
    required_approving_review_count: number | null;
    require_last_push_approval: boolean | null;
    dismissal_restrictions: object | null;
  };
  after: {
    url: string | null;
    dismiss_stale_reviews: boolean | null;
    require_code_owner_reviews: boolean | null;
    required_approving_review_count: number | null;
    require_last_push_approval: boolean | null;
    dismissal_restrictions: object | null;
  };
}
```

</details>


<details>
<summary><code>delete_pull_request_review_protection</code> — DESTRUCTIVE — REQUIRES EXPLICIT USER CONFIRMATION BEFORE CALLING.</summary>

DESTRUCTIVE — REQUIRES EXPLICIT USER CONFIRMATION BEFORE CALLING. Permanently removes the pull request review requirements from the given protected branch. This action is irreversible — the review requirement configuration (required approving review count, dismissal restrictions, code owner review requirement, and all other settings) cannot be recovered once deleted. NEVER call this tool autonomously or as part of an automated flow. You MUST stop, tell the user exactly what will be deleted and that it is permanent, and wait for their explicit written confirmation before proceeding.

**Inputs:**
```
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `branch` (string, required) — Branch name
```

**Output `data` schema:**

```typescript
{
  deleted: boolean | null;
  branch: string | null;
}
```

</details>


<details>
<summary><code>list_repository_rulesets</code> — List all rulesets for a repository.</summary>

List all rulesets for a repository.

**Inputs:**
```
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `includes_parents` (boolean, optional, default: true) — Include parent rulesets
- `per_page` (integer, optional, default: 30) — Results per page
- `page` (integer, optional, default: 1) — Page number
```

**Output `data` schema:**

```typescript
{
  rulesets: {
    id: number | null;
    name: string | null;
    target: string | null;
    source_type: string | null;
    enforcement: string | null;
    node_id: string | null;
    created_at: string | null;
    updated_at: string | null;
  }[];
  page: number | null;
  per_page: number | null;
}
```

</details>


<details>
<summary><code>get_repository_ruleset</code> — Get a specific ruleset for a repository.</summary>

Get a specific ruleset for a repository.

**Inputs:**
```
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `ruleset_id` (integer, required) — Ruleset ID
```

**Output `data` schema:**

```typescript
{
  id: number | null;
  name: string | null;
  target: string | null;
  source_type: string | null;
  source: string | null;
  enforcement: string | null;
  conditions: object | null;
  rules: object[];
  bypass_actors: object[];
  node_id: string | null;
  created_at: string | null;
  updated_at: string | null;
}
```

</details>


<details>
<summary><code>create_repository_ruleset</code> — Create a new ruleset for a repository.</summary>

Create a new ruleset for a repository.

**Inputs:**
```
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `name` (string, required) — Ruleset name
- `enforcement` (string, required) — active, evaluate, or disabled
- `target` (string, optional, default: "branch") — Target: branch, tag, or push
- `conditions` (object, optional) — Ruleset conditions
- `rules` (object[], optional) — Rules list
- `bypass_actors` (object[], optional) — Bypass actors
```

**Output `data` schema:**

```typescript
{
  id: number | null;
  name: string | null;
  target: string | null;
  enforcement: string | null;
  conditions: object | null;
  rules: object[];
  bypass_actors: object[];
  node_id: string | null;
  created_at: string | null;
  updated_at: string | null;
}
```

</details>


<details>
<summary><code>update_repository_ruleset</code> — Updates an existing repository ruleset.</summary>

Updates an existing repository ruleset. Only the fields you provide are changed — others keep their current value. NOTE: this overwrites the current field values — the original state is not stored after the call. The response includes both the before and after state so you have a full record of what changed.

**Inputs:**
```
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `ruleset_id` (integer, required) — Ruleset ID
- `name` (string, optional) — New ruleset name
- `enforcement` (string, optional) — active, evaluate, or disabled
- `target` (string, optional) — Updated target: branch, tag, or push
- `conditions` (object, optional) — Updated conditions
- `rules` (object[], optional) — Updated rules
- `bypass_actors` (object[], optional) — Updated bypass actors
```

**Output `data` schema:**

```typescript
{
  before: {
    id: number | null;
    name: string | null;
    target: string | null;
    source_type: string | null;
    source: string | null;
    enforcement: string | null;
    conditions: object | null;
    rules: object[];
    bypass_actors: object[];
    node_id: string | null;
    created_at: string | null;
    updated_at: string | null;
  };
  after: {
    id: number | null;
    name: string | null;
    target: string | null;
    enforcement: string | null;
    conditions: object | null;
    rules: object[];
    bypass_actors: object[];
    node_id: string | null;
    created_at: string | null;
    updated_at: string | null;
  };
}
```

</details>


<details>
<summary><code>delete_repository_ruleset</code> — DESTRUCTIVE — REQUIRES EXPLICIT USER CONFIRMATION BEFORE CALLING.</summary>

DESTRUCTIVE — REQUIRES EXPLICIT USER CONFIRMATION BEFORE CALLING. Permanently deletes the specified ruleset from the repository. This action is irreversible — the ruleset configuration (conditions, rules, and bypass actors) cannot be recovered once deleted. NEVER call this tool autonomously or as part of an automated flow. You MUST stop, tell the user exactly what will be deleted and that it is permanent, and wait for their explicit written confirmation before proceeding.

**Inputs:**
```
- `owner` (string, required) — Repository owner
- `repo` (string, required) — Repository name
- `ruleset_id` (integer, required) — Ruleset ID
```

**Output `data` schema:**

```typescript
{
  deleted: boolean | null;
  ruleset_id: number | null;
}
```

</details>


## API Parameters Reference

<details>
<summary><strong>Response Envelope</strong></summary>

Every tool returns the same top-level envelope. Only `data` varies per tool.

```json
// Success
{
  "success": true,
  "statusCode": 200,
  "retriable": false,
  "retry_after_seconds": null,
  "error": null,
  "data": { ... }
}

// Error
{
  "success": false,
  "statusCode": 400,
  "retriable": false,
  "retry_after_seconds": null,
  "error": { "code": "{ERROR_CODE}", "message": "{description}", "details": {} },
  "data": null
}
```

- `retriable` — `true` when it is safe to retry (rate limit, network error, 503). `false` for validation and auth errors.
- `retry_after_seconds` — seconds to wait before retrying; present only when `retriable` is `true` and the upstream specifies a delay.
- `error.code` — machine-readable string: `VALIDATION_ERROR`, `AUTH_ERROR`, `UPSTREAM_ERROR`, `SERVER_ERROR`.

</details>

<details>
<summary><strong>Common Parameters</strong></summary>

- `owner` — Repository owner, used across almost every tool that operates on a repository.
- `repo` — Repository name, paired with `owner` on almost every tool that operates on a repository.
- `page` — Page number for paginated list/search endpoints (default: 1 on all tools that support it).
- `perPage` / `per_page` — Items or results per page for paginated list/search endpoints (default: 30 where applicable; the parameter name varies by tool — see each tool's Inputs above).

</details>


<!-- OAuth provider: "Getting Your API Key" section intentionally omitted. -->


## Troubleshooting

<details>
<summary><strong>Missing or Invalid Headers</strong></summary>

- **Cause:** API key not provided in request headers or incorrect format
- **Solution:**
  1. Verify `Authorization: Bearer YOUR_API_KEY` and `X-Mewcp-Credential-Id: CREDENTIAL-ID` headers are present
  2. Check API key is active in your MewCP account

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
  2. Connect your GitHub account (OAuth) or add your API key (static)
  3. Retry the request with the correct `X-Mewcp-Credential-Id` header

</details>

<details>
<summary><strong>Malformed Request Payload</strong></summary>

- **Cause:** JSON payload is invalid or missing required fields
- **Solution:**
  1. Validate JSON syntax before sending
  2. Ensure all required tool parameters are included
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
  1. Check GitHub service status at [GitHub Status Page](https://www.githubstatus.com/)
  2. Verify your credential has the required permissions (OAuth scopes)
  3. Review the error message for specific details

</details>

---

<details>
<summary><strong>Resources</strong></summary>

- **[GitHub REST API Documentation](https://docs.github.com/en/rest)** — Official API reference
- **[GitHub REST API Endpoints](https://docs.github.com/en/rest/quickstart)** — Complete endpoint reference
- **[FastMCP Docs](https://gofastmcp.com/v2/getting-started/welcome)** — FastMCP specification
- **[FastMCP Credentials](https://pypi.org/project/fastmcp-credentials/)** — FastMCP Credentials package for credential handling


</details>
