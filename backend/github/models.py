"""Data structures returned by the GitHub integration."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class GitHubFile:
    """A file tracked in a specific revision of a GitHub repository."""

    path: str
    sha: str
    size: int
    url: str
