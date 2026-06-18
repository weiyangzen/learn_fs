# sources/storage-engines/pebble/.github/workflows/instrumented.yaml

## Purpose
`instrumented.yaml` defines reusable/manual nightly jobs for high-cost instrumented test variants: race, ASAN, and MSAN.

## Important APIs, types, and functions
Inputs include `sha`, `file_issue_branch`, and `go_version`. Jobs run `make testrace TAGS=`, `make testasan`, and `make testmsan`, with Go installed through `actions/setup-go`. ASAN uses Ubuntu 22.04 due to a noted Ubuntu 24.04/kernel issue. Failures call `post-issue`.

## Control flow
Each job independently checks out the requested SHA, installs Go, runs the relevant Make target, and conditionally files an issue on failure. Race runs on latest Ubuntu, ASAN is pinned to Ubuntu 22.04, and MSAN uses latest Ubuntu with Makefile-provided Clang configuration.

## State and persistence behavior
The workflow is read-only except for potential GitHub issue creation. Test binaries and sanitizer artifacts are transient runner state.

## Dependencies and integration points
Master and release nightlies call this workflow. It depends on Makefile sanitizer targets, Go compiler support for `-race`, `-asan`, and `-msan`, and runner toolchain availability.

## Risks and edge cases
Sanitizer support is sensitive to OS image changes. Race and sanitizer jobs are expensive and can time out if Makefile timeouts drift. `TAGS=` disables invariants for race, so it tests a different code shape than default invariant builds.

## Test signals
Passing race, ASAN, and MSAN jobs provide concurrency and memory-safety signals beyond normal unit tests. Failure issue content should identify branch, job, SHA, and Go version.
