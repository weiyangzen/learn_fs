# sources/sync-backup/syncthing/.github/workflows/org-members.yaml

Purpose: scheduled/manual workflow for organization membership recommendations.

Important APIs/types/functions: job `run-recommendation` runs the `ghcr.io/calmh/github-org-members:latest` container with environment variables for organization, token, ignored users, and extra repositories.

Control flow: on monthly schedule or manual dispatch, the job starts only for the Syncthing owner and delegates all logic to the container image.

State and persistence behavior: no repository state. Any recommendations or side effects are owned by the external tool and GitHub API.

Dependencies/integration: depends on `GOM_GITHUB_TOKEN`, `GOM_IGNORE_USERS`, `GOM_ALSO_REPOS`, GHCR image availability, and GitHub org/repo APIs.

Risks/test signals: use of a floating `latest` container can change behavior without a repository diff. The workflow has sensitive org/token context. Signal is a completed monthly run producing expected recommendation output.
