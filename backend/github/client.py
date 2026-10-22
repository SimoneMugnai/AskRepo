"""A small synchronous client for the GitHub REST API."""

from __future__ import annotations

import os
from typing import Any

import httpx

from .exceptions import GitHubClientError
from .models import GitHubFile


class GitHubClient:
    """Fetch repository metadata from GitHub.

    Public repositories work without a token. Setting ``GITHUB_TOKEN`` raises
    GitHub's rate limit and is required later for private repositories.
    """

    base_url = "https://api.github.com"

    def __init__(
        self,
        token: str | None = None,
        client: httpx.Client | None = None,
    ) -> None:
        resolved_token = token if token is not None else os.getenv("GITHUB_TOKEN")
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if resolved_token:
            headers["Authorization"] = f"Bearer {resolved_token}"

        # Dependency injection lets tests provide a mock transport and keeps
        # this class independent from command-line concerns.
        self._owns_client = client is None
        self._client = client or httpx.Client(
            base_url=self.base_url,
            headers=headers,
            timeout=20.0,
        )

    def __enter__(self) -> GitHubClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def close(self) -> None:
        """Close the underlying connection pool when this client owns it."""
        if self._owns_client:
            self._client.close()

    def list_files(
        self,
        owner: str,
        repository: str,
        ref: str = "HEAD",
    ) -> list[GitHubFile]:
        """Return every file in ``ref``, recursively, without downloading it.

        The Git Trees endpoint returns both directories and files. Restricting
        the result to ``blob`` entries gives the future ingestion filter only
        actual files to evaluate.
        """
        endpoint = f"/repos/{owner}/{repository}/git/trees/{ref}"
        try:
            response = self._client.get(endpoint, params={"recursive": "1"})
            response.raise_for_status()
        except httpx.HTTPError as error:
            raise GitHubClientError(
                f"Could not list files for {owner}/{repository}@{ref}."
            ) from error

        payload = response.json()
        if not isinstance(payload, dict) or not isinstance(payload.get("tree"), list):
            raise GitHubClientError("GitHub returned an unexpected tree response.")

        return [
            self._to_file(entry)
            for entry in payload["tree"]
            if isinstance(entry, dict) and entry.get("type") == "blob"
        ]

    @staticmethod
    def _to_file(entry: dict[str, Any]) -> GitHubFile:
        """Convert one GitHub tree entry after its type has been validated."""
        path = entry.get("path")
        sha = entry.get("sha")
        size = entry.get("size")
        url = entry.get("url")
        if not isinstance(path, str) or not isinstance(sha, str):
            raise GitHubClientError("GitHub returned a malformed file entry.")

        return GitHubFile(
            path=path,
            sha=sha,
            size=size if isinstance(size, int) else 0,
            url=url if isinstance(url, str) else "",
        )
