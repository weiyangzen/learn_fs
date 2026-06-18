<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/.github/workflows/go.yml -->
# sources/user-network-fs/go-nfs/.github/workflows/go.yml

## Purpose
Defines the go-nfs Go CI workflow.

## Important APIs, Types, and Functions
The workflow triggers on pushes and PRs to `master`, sets read-only contents permission, installs Go 1.x, checks out, gets deps, builds, runs golangci-lint, and tests the root package.

## Control Flow
Control flow is linear GitHub Actions steps in one Ubuntu job.

## State and Persistence Behavior
State is ephemeral CI workspace and module cache.

## Dependencies and Integration Points
Integrates with `actions/setup-go`, `actions/checkout`, `golangci-lint-action`, and `go test -v .`.

## Risks and Edge Cases
`go get -t -d` is dated, action versions are old, and only `go test .` runs rather than `./...`, so helpers/examples may not be covered.

## Test Signals
Signals are CI build/lint/test results on PRs and master pushes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/.github/workflows/go.yml -->
