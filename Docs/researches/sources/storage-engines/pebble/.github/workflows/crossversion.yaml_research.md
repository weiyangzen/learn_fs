# sources/storage-engines/pebble/.github/workflows/crossversion.yaml

## Purpose
`crossversion.yaml` is a reusable/manual workflow for running Pebble's cross-version smoke test against a chosen SHA and Go version.

## Important APIs, types, and functions
Inputs are `sha`, `file_issue_branch`, and `go_version`. Steps use `actions/checkout` with full history, `git fetch --all`, `actions/setup-go`, `scripts/crossversion_smoke_test.sh`, and the local `post-issue` action.

## Control flow
The workflow checks out the requested SHA, fetches all branches so release references are available, installs the requested Go version, and runs the cross-version smoke script. On failure, reusable nightly callers can file an issue labeled `C-test-failure`.

## State and persistence behavior
No repository state is persisted. Failure issue creation persists in GitHub if enabled by input.

## Dependencies and integration points
This job is called by master nightlies and may be run manually. It depends on release branches being available and on the cross-version script's internal expectations.

## Risks and edge cases
Full branch fetching can be slow or flaky. The smoke script likely depends on branch naming conventions. Missing `file_issue_branch` disables failure reporting, which is useful manually but can hide nightly failures if miswired.

## Test signals
Successful script completion across relevant release branches and correct failure issue creation are the core signals.
