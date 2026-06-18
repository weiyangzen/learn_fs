# sources/storage-engines/pebble/.github/workflows/tests.yaml

## Purpose
`tests.yaml` is the reusable/manual broad test workflow for Pebble, covering normal Linux, 32-bit, ARM, crossversion metadata, no-invariants, no-cgo, macOS, Windows, lint checks, and cross-architecture builds.

## Important APIs, types, and functions
Inputs are `sha`, `file_issue_branch`, and `go_version`. Jobs use `actions/checkout`, `actions/setup-go`, Makefile targets (`test`, `testobjiotracing`, `generate`, `crossversion-meta`, `testnocgo`, `mod-tidy-check`, `format-check`), direct `go test`, direct `go build`, and `post-issue`.

## Control flow
Each job checks out the requested SHA and installs the requested Go version. Linux runs main tests plus generation and workspace-clean assertion. Other jobs run architecture/build-mode variants: GOARCH=386, ARM runner tests, crossversion meta, no-invariants tags, no CGO, macOS, Windows, lint checks, and builds for mips/mipsle/mips64le/freebsd/netbsd/openbsd. Most jobs file branch-specific issues on failure.

## State and persistence behavior
The workflow is intended to be read-only; generation, formatting, and mod-tidy jobs fail if they produce diffs. Failure issues/comments may persist.

## Dependencies and integration points
It is called by release and master nightlies and can be manually dispatched. It depends on the Makefile, test scripts, generated-code checks, Git history for crossversion metadata, and platform runners.

## Risks and edge cases
Runner availability for `ubuntu-22.04-arm`, macOS, and Windows can be a source of infrastructure failure. `crossversion-meta` checks out release branches inside the job, so it must restore state correctly. Direct `go build` targets do not run tests but catch portability issues.

## Test signals
This workflow provides the main multi-platform signal. Clean workspace after generation, lint pass, no-cgo and no-invariants variants, and cross-OS/arch builds all indicate repository health beyond the default Linux test.
