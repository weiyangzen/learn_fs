<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/.github/workflows/vulncheck.yml -->
# sources/object-store/minio-mc/.github/workflows/vulncheck.yml

## Purpose
Security analysis workflow that runs Go vulnerability analysis on PRs and master pushes.

## Important APIs, types, and functions
Checks out code, sets up Go 1.25.x, installs `golang.org/x/vuln/cmd/govulncheck@latest`, and runs `govulncheck ./...`.

## Control flow
Single Ubuntu job performs setup, install, and analysis sequentially.

## State and persistence behavior
No persistent state. It reads module dependencies and reports vulnerabilities in CI.

## Dependencies and integration points
Depends on Go module resolution, the latest govulncheck, and GitHub Actions.

## Risks and test signals
Using `@latest` can introduce nondeterministic failures when govulncheck changes. Signal is a clean vulnerability scan or actionable CI failure.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/.github/workflows/vulncheck.yml -->
