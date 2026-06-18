## sources/user-network-fs/gcsfuse/.github/dependabot.yml

Purpose: Configures Dependabot dependency update PRs.

Important APIs/types/functions: version 2 with beta ecosystems enabled. Defines weekly updates for Docker at `/`, Go modules at `/` limited to direct dependencies and grouped as `go-dependencies`, and pip at `/` grouped as `python-dependencies`.

Control flow: declarative scheduling by Dependabot. Grouping coalesces matching updates into single PRs per ecosystem group.

State and persistence: creates GitHub PRs/branches and metadata, but no local state by itself.

Dependencies and integration points: integrates with GitHub Dependabot and repository manifests such as Dockerfile, Go modules, and Python requirements/setup files.

Risks: Go indirect dependencies are excluded, so transitive security updates may depend on direct dependency bumps. Grouped PRs reduce noise but can make dependency failures harder to isolate.

Test signals: Dependabot weekly PR activity and successful CI on generated update branches.
