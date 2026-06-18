# sources/storage-engines/pebble/.github/workflows/ci.yaml

## Purpose
`ci.yaml` defines Pebble's pull-request and protected-branch test workflow, including required Linux tests, lint checks, no-cgo/no-invariants variants, race tests, macOS tests, and stress of newly added tests on PRs.

## Important APIs, types, and functions
The workflow triggers on pushes and pull requests to `master`, `crl-release-*`, and `pebble-release-*`. Jobs use `actions/checkout`, `actions/setup-go`, `make` targets such as `test`, `testobjiotracing`, `generate`, `mod-tidy-check`, `format-check`, `testnocgo`, and `testrace`, plus `scripts/stress-new-tests.sh`.

## Control flow
Each job checks out the repository, installs Go 1.26, and runs its target. The main Linux job also asserts a clean workspace after generation. The PR-only stress job fetches full history, installs `cockroachdb/stress`, sets `BASE_BRANCH`, and runs a script to stress tests added by the PR.

## State and persistence behavior
The workflow does not persist repository state, but generation and formatting checks intentionally fail if source changes are produced. It consumes GitHub runner state and may populate Go module/build caches implicitly.

## Dependencies and integration points
It is the primary integration point between repository code and GitHub branch protection. It relies on Makefile targets, Go 1.26, shell scripts, and GitHub-hosted Linux/macOS runners.

## Risks and edge cases
Required jobs must retain stable names. `make generate` can be expensive and must keep the workspace clean. PR stress uses `fetch-depth: 0` and `gh`, which depend on GitHub token behavior. Go version drift must stay aligned with the repo.

## Test signals
Passing required jobs, clean workspace checks, race/no-cgo/no-invariants variants, macOS coverage, and stress-new-tests output are the central CI signals.
