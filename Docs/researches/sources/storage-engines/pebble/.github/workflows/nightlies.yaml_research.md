# sources/storage-engines/pebble/.github/workflows/nightlies.yaml

## Purpose
`nightlies.yaml` orchestrates manual master-branch nightly coverage by calling reusable workflows for tests, architecture coverage, stress, instrumented variants, custom Cockroach Go, crossversion, and an `iterv2` tag variant.

## Important APIs, types, and functions
Jobs call `tests.yaml`, `s390x.yaml`, `stress.yaml`, `instrumented.yaml`, `cockroach-go.yaml`, and `crossversion.yaml`, each with a one-element Go 1.26 matrix. The local `linux-iterv2` job runs `make test TAGS="invariants iterv2"`, checks workspace cleanliness, and files an issue on failure.

## Control flow
Manual dispatch runs all jobs independently with `fail-fast: false` where matrices are used. Reusable jobs receive `sha: github.sha` and `file_issue_branch: master`. The Cockroach Go job pins `go_branch: cockroach-go1.26.2`. The `linux-iterv2` job checks out the repository, installs Go, runs tagged tests, asserts clean workspace, and posts issues on failure.

## State and persistence behavior
Persistent state is limited to failure issues/comments. Test outputs are transient runner state.

## Dependencies and integration points
This is the top-level master nightly orchestrator and depends on all reusable workflow files, Makefile targets, the local post-issue action, and the Cockroach Go fork branch.

## Risks and edge cases
It is manual-only, so scheduled master nightly coverage must be triggered elsewhere or by humans. Hardcoded custom Go branch and Go matrix need updates with compiler upgrades. `iterv2` coverage is local to this workflow and not shared with release nightlies.

## Test signals
The workflow aggregates the broadest master health signal: platform tests, stress, sanitizer/race, custom Go, crossversion, and iterator-v2 tagged tests.
