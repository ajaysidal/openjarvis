"""GitHub connector — recent activity via REST API.

Uses OAuth2 tokens stored locally.
"""

from __future__ import annotations

import base64
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterator, Optional, List

import httpx

from silas.connectors._stubs import BaseConnector, Document, SyncStatus
from silas.core.config import DEFAULT_CONFIG_DIR
from silas.core.registry import ConnectorRegistry

_GITHUB_API_BASE = "https://api.github.com"
_DEFAULT_TOKEN_PATH = str(DEFAULT_CONFIG_DIR / "connectors" / "github.json")


def _github_api_get(
    token: str, endpoint: str, params: Optional[Dict[str, Any]] = None
) -> Any:
    """Call a GitHub API endpoint."""
    resp = httpx.get(
        f"{_GITHUB_API_BASE}/{endpoint}",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "OpenJarvis-GitHubConnector",
        },
        params=params or {},
        timeout=30.0,
    )
    resp.raise_for_status()
    return resp.json()


def _github_api_post(
    token: str, endpoint: str, data: Optional[Dict[str, Any]] = None
) -> Any:
    """Call a GitHub API endpoint with POST."""
    resp = httpx.post(
        f"{_GITHUB_API_BASE}/{endpoint}",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "OpenJarvis-GitHubConnector",
        },
        json=data or {},
        timeout=30.0,
    )
    resp.raise_for_status()
    return resp.json()


def _github_api_patch(
    token: str, endpoint: str, data: Optional[Dict[str, Any]] = None
) -> Any:
    """Call a GitHub API endpoint with PATCH."""
    resp = httpx.patch(
        f"{_GITHUB_API_BASE}/{endpoint}",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "OpenJarvis-GitHubConnector",
        },
        json=data or {},
        timeout=30.0,
    )
    resp.raise_for_status()
    return resp.json()


def _github_api_put(
    token: str, endpoint: str, data: Optional[Dict[str, Any]] = None
) -> Any:
    """Call a GitHub API endpoint with PUT."""
    resp = httpx.put(
        f"{_GITHUB_API_BASE}/{endpoint}",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "OpenJarvis-GitHubConnector",
        },
        json=data or {},
        timeout=30.0,
    )
    resp.raise_for_status()
    return resp.json()


def _github_api_delete(
    token: str, endpoint: str
) -> Any:
    """Call a GitHub API endpoint with DELETE."""
    resp = httpx.delete(
        f"{_GITHUB_API_BASE}/{endpoint}",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "OpenJarvis-GitHubConnector",
        },
        timeout=30.0,
    )
    resp.raise_for_status()
    return resp.json()


@ConnectorRegistry.register("github")
class GitHubConnector(BaseConnector):
    """Sync recent activity from GitHub."""

    connector_id = "github"
    display_name = "GitHub"
    auth_type = "oauth"

    def __init__(self, *, token_path: str = _DEFAULT_TOKEN_PATH) -> None:
        self._token_path = Path(token_path)
        self._status = SyncStatus()

    def _load_tokens(self) -> Dict[str, str]:
        return json.loads(self._token_path.read_text(encoding="utf-8"))

    def _save_tokens(self, tokens: Dict[str, str]) -> None:
        from silas.security.file_utils import secure_write_json

        secure_write_json(self._token_path, tokens)

    def _get_access_token(self) -> str:
        tokens = self._load_tokens()
        return tokens["access_token"]

    def is_connected(self) -> bool:
        try:
            access_token = self._load_tokens().get("access_token")
        except (OSError, json.JSONDecodeError):
            return False
        return isinstance(access_token, str) and bool(access_token.strip())

    def disconnect(self) -> None:
        if self._token_path.exists():
            self._token_path.unlink()

    def auth_url(self) -> str:
        """Return GitHub OAuth authorization URL."""
        from urllib.parse import urlencode

        from silas.connectors.oauth import (
            get_client_credentials,
            get_provider_for_connector,
        )

        provider = get_provider_for_connector("github")
        if not provider:
            return "https://github.com/settings/applications/new"
        creds = get_client_credentials(provider)
        if not creds:
            return "https://github.com/settings/applications/new"
        client_id, _ = creds
        redirect_uri = f"http://{provider.callback_host}:{provider.callback_port}{provider.callback_path}"
        params = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": " ".join(provider.scopes),
        }
        return f"{provider.auth_endpoint}?{urlencode(params)}"

    def handle_callback(self, code: str) -> None:
        """Exchange authorization code for tokens and save."""
        from silas.connectors.oauth import (
            _CONNECTORS_DIR,
            _exchange_token,
            get_client_credentials,
            get_provider_for_connector,
            require_access_token,
            save_tokens,
        )

        provider = get_provider_for_connector("github")
        creds = get_client_credentials(provider) if provider else None
        if not provider or not creds:
            raise RuntimeError("GitHub client credentials not configured")
        client_id, client_secret = creds
        redirect_uri = f"http://{provider.callback_host}:{provider.callback_port}{provider.callback_path}"
        tokens = _exchange_token(provider, code, client_id, client_secret, redirect_uri)
        access_token = require_access_token(tokens)
        payload = {
            "access_token": access_token,
            "refresh_token": tokens.get("refresh_token", ""),
            "client_id": client_id,
            "client_secret": client_secret,
        }
        for filename in provider.credential_files:
            save_tokens(str(_CONNECTORS_DIR / filename), payload)

    def sync(
        self, *, since: Optional[datetime] = None, cursor: Optional[str] = None
    ) -> Iterator[Document]:
        """Sync recent activity from GitHub.

        Yields Documents for:
        - User's repositories
        - Recent issues (if since provided)
        - Recent pull requests
        - Recent commits (optional, we'll do for now)
        """
        token = self._get_access_token()
        self._status.state = "syncing"
        self._status.error = None  # Clear any previous error

        # Fetch user's repositories
        try:
            repos = _github_api_get(token, "user/repos", params={"sort": "updated", "per_page": "100"})
        except httpx.HTTPStatusError as e:
            self._status.state = "error"
            self._status.error = f"Failed to fetch repositories: {e.response.status_code} {e.response.text}"
            raise

        for repo in repos:
            repo_doc_id = f"github-repo-{repo['id']}"
            yield Document(
                doc_id=repo_doc_id,
                source="github",
                doc_type="repository",
                title=repo["full_name"],
                content=json.dumps(repo),
                timestamp=datetime.fromisoformat(repo["updated_at"].replace("Z", "+00:00")),
                url=repo["html_url"],
                metadata={
                    "repo_id": repo["id"],
                    "owner": repo["owner"]["login"],
                    "private": repo["private"],
                    "language": repo["language"],
                    "stars": repo["stargazers_count"],
                    "forks": repo["forks_count"],
                    "open_issues": repo["open_issues_count"],
                },
            )

        # Fetch recent issues if since is provided
        if since:
            try:
                # We'll fetch issues from the user's repositories (since we don't have a global issues endpoint without scope)
                # Instead, we can use the issues endpoint for the authenticated user: https://api.github.com/issues
                # This lists issues assigned to the user across repositories.
                params = {
                    "since": since.isoformat(),
                    "per_page": "100",
                }
                issues = _github_api_get(token, "issues", params=params)
            except httpx.HTTPStatusError as e:
                self._status.state = "error"
                self._status.error = f"Failed to fetch issues: {e.response.status_code} {e.response.text}"
                raise

            for issue in issues:
                # Skip pull requests (they appear in issues endpoint but are not issues)
                if "pull_request" in issue:
                    continue
                issue_doc_id = f"github-issue-{issue['id']}"
                yield Document(
                    doc_id=issue_doc_id,
                    source="github",
                    doc_type="issue",
                    title=issue["title"],
                    content=json.dumps(issue),
                    timestamp=datetime.fromisoformat(issue["updated_at"].replace("Z", "+00:00")),
                    url=issue["html_url"],
                    metadata={
                        "issue_id": issue["id"],
                        "repo": issue["repository_url"].split("/")[-2] + "/" + issue["repository_url"].split("/")[-1],
                        "number": issue["number"],
                        "state": issue["state"],
                        "author": issue["user"]["login"],
                        "assignee": issue["assignee"]["login"] if issue["assignee"] else None,
                        "labels": [label["name"] for label in issue["labels"]],
                    },
                )

        # Fetch recent pull requests
        # We'll limit to 5 repositories to avoid too many requests
        for repo in repos[:5]:
            owner = repo["owner"]["login"]
            repo_name = repo["name"]
            try:
                params = {"state": "all", "sort": "updated", "direction": "desc", "per_page": "10"}
                if since:
                    params["since"] = since.isoformat()
                pulls = _github_api_get(
                    token,
                    f"repos/{owner}/{repo_name}/pulls",
                    params=params,
                )
            except httpx.HTTPStatusError as e:
                # If we get rate limited, we should wait? But for simplicity, we'll skip this repo and continue.
                # We'll set an error in the status but not break the whole sync.
                self._status.error = f"Failed to fetch pull requests for {owner}/{repo_name}: {e.response.status_code}"
                continue

            for pr in pulls:
                pr_doc_id = f"github-pr-{pr['id']}"
                yield Document(
                    doc_id=pr_doc_id,
                    source="github",
                    doc_type="pull_request",
                    title=pr["title"],
                    content=json.dumps(pr),
                    timestamp=datetime.fromisoformat(pr["updated_at"].replace("Z", "+00:00")),
                    url=pr["html_url"],
                    metadata={
                        "pr_id": pr["id"],
                        "repo": f"{owner}/{repo_name}",
                        "number": pr["number"],
                        "state": pr["state"],
                        "author": pr["user"]["login"],
                        "merged": pr["merged"],
                        "mergeable": pr["mergeable"],
                    },
                )

        # Fetch recent commits (optional) - we'll do for the user's own repositories (limited)
        for repo in repos[:5]:  # Limit to 5 repositories
            owner = repo["owner"]["login"]
            repo_name = repo["name"]
            try:
                commits = _github_api_get(
                    token,
                    f"repos/{owner}/{repo_name}/commits",
                    params={"since": since.isoformat() if since else None, "per_page": "10"},
                )
            except httpx.HTTPStatusError as e:
                self._status.error = f"Failed to fetch commits for {owner}/{repo_name}: {e.response.status_code}"
                continue

            for commit in commits:
                commit_doc_id = f"github-commit-{commit['sha']}"
                yield Document(
                    doc_id=commit_doc_id,
                    source="github",
                    doc_type="commit",
                    title=commit["commit"]["message"].split("\n")[0][:100],  # First line, truncated
                    content=json.dumps(commit),
                    timestamp=datetime.fromisoformat(commit["commit"]["committer"]["date"].replace("Z", "+00:00")),
                    url=commit["html_url"],
                    metadata={
                        "sha": commit["sha"],
                        "repo": f"{owner}/{repo_name}",
                        "author": commit["commit"]["author"]["name"],
                        "author_email": commit["commit"]["author"]["email"],
                    },
                )

        self._status.state = "idle"
        self._status.last_sync = datetime.now()

    # Helper methods as requested

    def get_repository_details(self, owner: str, repo: str) -> Dict[str, Any]:
        """Get details for a specific repository."""
        token = self._get_access_token()
        return _github_api_get(token, f"repos/{owner}/{repo}")

    def get_file_contents(self, owner: str, repo: str, path: str, ref: Optional[str] = None) -> Dict[str, Any]:
        """Get the contents of a file in a repository."""
        token = self._get_access_token()
        params = {}
        if ref:
            params["ref"] = ref
        return _github_api_get(token, f"repos/{owner}/{repo}/contents/{path}", params=params)

    def create_file(
        self, owner: str, repo: str, path: str, content: str, message: str, branch: str
    ) -> Dict[str, Any]:
        """Create a new file in a repository."""
        token = self._get_access_token()
        # GitHub API expects base64 encoded content
        encoded_content = base64.b64encode(content.encode("utf-8")).decode("utf-8")
        data = {
            "message": message,
            "content": encoded_content,
            "branch": branch,
        }
        return _github_api_put(token, f"repos/{owner}/{repo}/contents/{path}", data=data)

    def update_file(
        self,
        owner: str,
        repo: str,
        path: str,
        content: str,
        message: str,
        branch: str,
        sha: str,
    ) -> Dict[str, Any]:
        """Update an existing file in a repository."""
        token = self._get_access_token()
        # GitHub API expects base64 encoded content
        encoded_content = base64.b64encode(content.encode("utf-8")).decode("utf-8")
        data = {
            "message": message,
            "content": encoded_content,
            "branch": branch,
            "sha": sha,
        }
        return _github_api_put(token, f"repos/{owner}/{repo}/contents/{path}", data=data)

    def list_issues(
        self,
        owner: str,
        repo: str,
        state: str = "open",
        labels: Optional[List[str]] = None,
        since: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """List issues in a repository."""
        token = self._get_access_token()
        params: Dict[str, Any] = {"state": state}
        if labels:
            params["labels"] = ",".join(labels)
        if since:
            params["since"] = since.isoformat()
        return _github_api_get(token, f"repos/{owner}/{repo}/issues", params=params)

    def create_issue(
        self,
        owner: str,
        repo: str,
        title: str,
        body: Optional[str] = None,
        labels: Optional[List[str]] = None,
        assignee: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create an issue in a repository."""
        token = self._get_access_token()
        data: Dict[str, Any] = {"title": title}
        if body is not None:
            data["body"] = body
        if labels:
            data["labels"] = labels
        if assignee:
            data["assignee"] = assignee
        return _github_api_post(token, f"repos/{owner}/{repo}/issues", data=data)

    def list_pull_requests(
        self,
        owner: str,
        repo: str,
        state: str = "open",
        sort: str = "created",
        direction: str = "desc",
    ) -> List[Dict[str, Any]]:
        """List pull requests in a repository."""
        token = self._get_access_token()
        params = {
            "state": state,
            "sort": sort,
            "direction": direction,
        }
        return _github_api_get(token, f"repos/{owner}/{repo}/pulls", params=params)

    def search_code(
        self, query: str, sort: str = "indexed", order: str = "desc"
    ) -> List[Dict[str, Any]]:
        """Search for code across GitHub."""
        token = self._get_access_token()
        params = {
            "q": query,
            "sort": sort,
            "order": order,
            "per_page": "100",
        }
        # Note: The search endpoint returns a different structure with 'total_count' and 'items'
        result = _github_api_get(token, "search/code", params=params)
        return result.get("items", [])

    def search_issues(
        self, query: str, sort: str = "created", order: str = "desc"
    ) -> List[Dict[str, Any]]:
        """Search for issues across GitHub."""
        token = self._get_access_token()
        params = {
            "q": query,
            "sort": sort,
            "order": order,
            "per_page": "100",
        }
        result = _github_api_get(token, "search/issues", params=params)
        return result.get("items", [])

    def list_codespaces(self) -> List[Dict[str, Any]]:
        """List codespaces for the authenticated user."""
        token = self._get_access_token()
        return _github_api_get(token, "user/codespaces")

    def create_codespace(
        self, display_name: str, repo: str, branch: str, machine: str
    ) -> Dict[str, Any]:
        """Create a new codespace."""
        token = self._get_access_token()
        data = {
            "display_name": display_name,
            "repository": repo,
            "branch": branch,
            "machine": machine,
        }
        return _github_api_post(token, "user/codespaces", data=data)

    def list_workflow_runs(
        self,
        owner: str,
        repo: str,
        workflow_id: Optional[str] = None,
        event: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List workflow runs for a repository."""
        token = self._get_access_token()
        params: Dict[str, Any] = {}
        if workflow_id:
            params["workflow_id"] = workflow_id
        if event:
            params["event"] = event
        if status:
            params["status"] = status
        return _github_api_get(token, f"repos/{owner}/{repo}/actions/runs", params=params)

    def sync_status(self) -> SyncStatus:
        return self._status
