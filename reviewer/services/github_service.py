import logging
from typing import Any

import requests
from django.conf import settings

from .exceptions import GitHubServiceError

logger = logging.getLogger(__name__)


class GitHubService:
    def __init__(self) -> None:
        self.base_url = settings.GITHUB_API_BASE_URL.rstrip("/")
        self.timeout = settings.GITHUB_TIMEOUT_SECONDS
        self.token = settings.GITHUB_TOKEN

    def _headers(self) -> dict[str, str]:
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def fetch_pr_details(self, repo: str, pull_number: int) -> dict[str, Any]:
        url = f"{self.base_url}/repos/{repo}/pulls/{pull_number}"
        return self._get_json(url, context="fetch_pr_details")

    def fetch_pr_files(self, repo: str, pull_number: int) -> list[dict[str, Any]]:
        url = f"{self.base_url}/repos/{repo}/pulls/{pull_number}/files"
        files = self._get_json(url, context="fetch_pr_files")
        if not isinstance(files, list):
            raise GitHubServiceError("Unexpected response shape from GitHub files API.")
        return files

    def post_pr_comment(
        self,
        repo: str,
        pull_number: int,
        body: str,
        path: str | None = None,
        line: int | None = None,
        commit_id: str | None = None,
    ) -> dict[str, Any]:
        if path and line and commit_id:
            url = f"{self.base_url}/repos/{repo}/pulls/{pull_number}/comments"
            payload: dict[str, Any] = {
                "body": body,
                "commit_id": commit_id,
                "path": path,
                "line": line,
            }
        else:
            # Falls back to a generic PR issue comment.
            url = f"{self.base_url}/repos/{repo}/issues/{pull_number}/comments"
            payload = {"body": body}

        logger.info("Posting PR comment to %s#%s", repo, pull_number)
        try:
            response = requests.post(
                url,
                headers=self._headers(),
                json=payload,
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            raise GitHubServiceError("Unable to reach GitHub API while posting comment.") from exc

        if response.status_code >= 400:
            raise GitHubServiceError(
                f"GitHub comment API failed with status {response.status_code}: {response.text}"
            )
        return response.json()

    def _get_json(self, url: str, context: str) -> dict[str, Any] | list[dict[str, Any]]:
        logger.info("GitHub API call (%s): %s", context, url)
        try:
            response = requests.get(url, headers=self._headers(), timeout=self.timeout)
        except requests.RequestException as exc:
            raise GitHubServiceError(f"Unable to reach GitHub API during {context}.") from exc

        if response.status_code >= 400:
            raise GitHubServiceError(
                f"GitHub API failed during {context} with status {response.status_code}: {response.text}"
            )

        try:
            return response.json()
        except ValueError as exc:
            raise GitHubServiceError(f"GitHub API returned invalid JSON during {context}.") from exc
