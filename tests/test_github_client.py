"""Tests for the first GitHub API operation."""

import httpx

from backend.github.client import GitHubClient


def test_list_files_returns_only_file_entries() -> None:
    """Directories from GitHub's tree response must not enter ingestion."""
    transport = httpx.MockTransport(
        lambda request: httpx.Response(
            200,
            json={
                "tree": [
                    {"path": "src", "type": "tree", "sha": "directory"},
                    {
                        "path": "src/app.py",
                        "type": "blob",
                        "sha": "file-sha",
                        "size": 42,
                        "url": "https://api.github.com/file",
                    },
                ]
            },
        )
    )
    http_client = httpx.Client(
        base_url="https://api.github.com",
        transport=transport,
    )
    client = GitHubClient(client=http_client)

    files = client.list_files("octocat", "hello-world", ref="main")

    assert files[0].path == "src/app.py"
    assert files[0].sha == "file-sha"
    assert len(files) == 1
