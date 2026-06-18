# sources/sync-backup/restic/.github/dependabot.yml

Purpose: Dependabot configuration for restic dependency update automation.

Control flow/state: version 2 config schedules monthly checks for Go module dependencies in `/` and GitHub Actions dependencies in `/`. It groups `golang.org/x/*` module updates under `golang-x-deps`.

Dependencies/integration: consumed by GitHub Dependabot. It interacts with `go.mod`, `go.sum`, and workflow action references, then creates pull requests when updates are available.

Risks/test signals: monthly cadence can delay security updates. Only `golang.org/x/*` dependencies are grouped; other ecosystems may create separate PRs. Validation occurs through Dependabot logs and generated PRs.
