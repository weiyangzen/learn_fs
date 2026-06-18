# sources/sync-backup/restic/.github/workflows/codespell.yml

Purpose: GitHub Actions workflow that checks spelling with codespell.

Control flow/state: runs on pushes to `master`, pull requests, and merge queue events. It grants read-only contents permission, checks out the repository, then invokes a pinned `codespell-project/actions-codespell` action. Codespell's detailed settings live in `.codespellrc`.

Dependencies/integration: depends on GitHub Actions, `actions/checkout@v6`, and the pinned codespell action. It is a quality gate for text/code spelling regressions.

Risks/test signals: the third-party action is pinned by commit, reducing supply-chain drift but requiring manual updates. The workflow is small and has no repository mutations. A passing job is the validation signal.
