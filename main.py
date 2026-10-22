from __future__ import annotations

import argparse

from backend.github.client import GitHubClient


def main() -> None:
    """List the files tracked in a GitHub repository."""
    parser = argparse.ArgumentParser(description="Inspect a GitHub repository")
    parser.add_argument("owner", help="GitHub account or organization")
    parser.add_argument("repository", help="Repository name")
    parser.add_argument(
        "--ref",
        default="HEAD",
        help="Branch, tag, or commit to inspect (default: HEAD)",
    )
    arguments = parser.parse_args()

    with GitHubClient() as client:
        files = client.list_files(
            owner=arguments.owner,
            repository=arguments.repository,
            ref=arguments.ref,
        )

    for file in files:
        print(file.path)

    print(f"\nFound {len(files)} files.")


if __name__ == "__main__":
    main()
