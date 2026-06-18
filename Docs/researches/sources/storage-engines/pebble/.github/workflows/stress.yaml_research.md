# sources/storage-engines/pebble/.github/workflows/stress.yaml

## Purpose
`stress.yaml` runs Pebble unit tests under CockroachDB's `stress` tool for nightly flake discovery.

## Important APIs, types, and functions
Inputs are `sha`, `file_issue_branch`, and `go_version`. Steps use `actions/checkout`, `actions/setup-go`, `go install github.com/cockroachdb/stress@latest`, `scripts/stress.sh`, and the local `post-issue` action.

## Control flow
The workflow checks out the requested SHA, installs Go, installs the stress binary into the Go toolchain path, runs the repository stress script, and conditionally files a failure issue.

## State and persistence behavior
The workflow mutates only transient runner tool state by installing `stress`. Failure issue creation is persistent when enabled.

## Dependencies and integration points
Release and master nightlies call this reusable workflow. It depends on the external stress module, the repository's stress script, and Go version compatibility.

## Risks and edge cases
Installing `stress@latest` can introduce nondeterminism if the tool changes. Stress runs are time/resource intensive and can produce flaky failures that need triage. Missing issue permissions from callers can make failure reporting fail.

## Test signals
Signals include repeated test pass under stress, clear failure logs for flakes, and issue creation with branch/SHA/Go context.
