# sources/sync-backup/git-lfs/.github/dependabot.yml

Purpose: Dependabot configuration for git-lfs dependency update pull requests.

Important APIs/types/functions: Dependabot `version: 2`; two update entries for `github-actions` at `/` and `gomod` at `/`, both scheduled monthly.

Control flow: Dependabot periodically scans GitHub Actions workflow dependencies and Go module dependencies in the repository root and opens update PRs according to the monthly interval.

State/persistence behavior: no repository runtime state; Dependabot creates external PRs and branch state when updates are available.

Dependencies/integration: integrates with GitHub Dependabot and the repo's GitHub Actions and Go module ecosystem.

Risks/test signals: monthly cadence may batch multiple updates and increase CI/release workflow churn. Signals are successful Dependabot PR creation, CI pass on update PRs, and absence of unsupported ecosystem/directory errors.
