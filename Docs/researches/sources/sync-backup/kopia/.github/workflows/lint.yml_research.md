# sources/sync-backup/kopia/.github/workflows/lint.yml

## Purpose
Runs static analysis, vulnerability checking, formatting checks, lock checks, and cross-OS lint coverage for pull requests to `master`.

## APIs, Control Flow, and Integration Points
The workflow declares read-only repository permissions by default, then grants `security-events: write` at the job level so SARIF can be uploaded. The matrix runs on Ubuntu and macOS. Each job installs Go, runs `govulncheck` twice to produce SARIF and fail on findings, uploads the SARIF via CodeQL, then delegates to `make lint`, `make lint-windows` on Ubuntu, `make check-locks`, and `make check-prettier`.

## State, Persistence, and Dependencies
It creates `govulncheck.sarif`, uses pinned GitHub actions, and relies on the top-level Makefile plus `.golangci.yml` for lint policy. Shared environment variables enable Makefile behavior and optional filename-stress modes controlled by secrets.

## Risks and Test Signals
The workflow grants SARIF upload permission even on macOS; this is required for CodeQL upload but should remain scoped. `govulncheck` is installed at a fixed version, which improves reproducibility but can stale vulnerability knowledge. The signal is broad: Go vulnerability analysis, golangci-lint, Windows cross-linting, custom lock vetting, and app Prettier checks all run before merge.
