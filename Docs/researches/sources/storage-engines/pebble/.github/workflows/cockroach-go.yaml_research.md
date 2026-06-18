# sources/storage-engines/pebble/.github/workflows/cockroach-go.yaml

## Purpose
This reusable/manual workflow runs Pebble tests with a CockroachDB-maintained Go fork branch, mainly for nightly compatibility with custom Go toolchains.

## Important APIs, types, and functions
Inputs include `sha`, `file_issue_branch`, `bootstrap_go_version`, and required `go_branch`. It uses `git ls-remote` to resolve the fork branch SHA, `actions/cache` for toolchain caching under `~/.cache/cockroachdb-go/<sha>`, `actions/setup-go` for bootstrap Go, `scripts/run-tests-with-custom-go.sh`, and the local `post-issue` action.

## Control flow
The workflow checks out the requested repository SHA, resolves the custom Go branch tip, restores a cache keyed by that SHA, installs bootstrap Go, and runs all tests with invariants tags through the custom toolchain script. On failure and when `file_issue_branch` is provided, it creates or updates a nightly failure issue.

## State and persistence behavior
Persistent external state is the GitHub Actions cache for the custom toolchain and any GitHub issue/comment created on failure. Repository state is read-only within the run.

## Dependencies and integration points
It integrates master nightlies with `nightlies.yaml`, the CockroachDB Go fork repository, Make/script-based test execution, and issue reporting.

## Risks and edge cases
`git ls-remote` can fail or return an empty SHA for invalid branches. Cache poisoning or stale custom toolchains could affect results if the script does not validate contents. Failure filing depends on issue write permissions inherited from the caller.

## Test signals
Signals include successful custom toolchain resolution, cache hit/miss behavior, test completion under `-tags invariants`, and issue creation on forced failures.
