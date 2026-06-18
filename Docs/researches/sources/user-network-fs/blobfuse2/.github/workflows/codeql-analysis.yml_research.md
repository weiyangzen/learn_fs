# sources/user-network-fs/blobfuse2/.github/workflows/codeql-analysis.yml

## Purpose
This workflow runs GitHub CodeQL analysis for Go code on pushes and pull requests targeting `main`.

## Important APIs, Types, and Functions
It uses `actions/checkout@v6`, `github/codeql-action/init@v4`, `github/codeql-action/autobuild@v4`, and `github/codeql-action/analyze@v4` with matrix language `go`.

## Control Flow
For each trigger, the job checks out the repository, initializes CodeQL for Go, lets CodeQL autobuild the project, and uploads analysis results to GitHub security events.

## State and Persistence Behavior
The workflow creates CodeQL databases and build artifacts on the runner and persists SARIF/security findings into GitHub's code scanning backend.

## Dependencies and Integration Points
It integrates with GitHub code scanning and depends on the Go project being autobuildable on `ubuntu-latest`. The job has `security-events: write` permission.

## Risks and Edge Cases
Autobuild may miss CGO/FUSE-specific build requirements or build tags used by Azure DevOps. There is no custom query config or manual build fallback enabled.

## Test Signals
Signals include CodeQL database creation, successful autobuild, and code scanning alerts appearing or updating in GitHub Security.
