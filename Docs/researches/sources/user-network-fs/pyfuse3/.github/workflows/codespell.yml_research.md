## sources/user-network-fs/pyfuse3/.github/workflows/codespell.yml

Purpose: GitHub Actions workflow for spelling checks.

Important APIs/types/functions: Runs on pushes and pull requests to `main`, grants read-only contents permission, checks out code, then runs `codespell-project/actions-codespell@v2`. The file notes configuration is in `pyproject.toml`.

Control flow: Single job on Ubuntu latest with checkout then codespell action.

State and persistence: No persistent state beyond CI results.

Dependencies and integration: Integrates repository spelling policy with GitHub Actions.

Risks and test signals: If `pyproject.toml` config drifts or action version changes behavior, false positives can block PRs. Test by running codespell locally or in CI.
