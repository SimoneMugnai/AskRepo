"""GitHub integration used by the ingestion pipeline."""

from .client import GitHubClient
from .models import GitHubFile

__all__ = ["GitHubClient", "GitHubFile"]
