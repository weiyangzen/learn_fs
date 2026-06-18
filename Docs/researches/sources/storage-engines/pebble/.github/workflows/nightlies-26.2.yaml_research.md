# sources/storage-engines/pebble/.github/workflows/nightlies-26.2.yaml

## Purpose
This workflow schedules daily nightly testing for branch `crl-release-26.2`.

## Important APIs, types, and functions
It uses the shared release-nightly pattern with `BRANCH=crl-release-26.2`, a `resolve-sha` job, and calls to `tests.yaml`, `s390x.yaml`, `stress.yaml`, and `instrumented.yaml` using Go 1.25.

## Control flow
The resolver checks out full history and records the branch name plus `git rev-parse origin/$BRANCH`. All child workflows depend on that output and include `file_issue_branch` so failure issues identify the release line.

## State and persistence behavior
The workflow is read-only apart from downstream issue/comment creation on test failure.

## Dependencies and integration points
It connects the latest listed release branch to the repository's reusable nightly test suite and GitHub issue reporting action.

## Risks and edge cases
Hardcoded branch and Go version must track release policy. If reusable workflow names or inputs change, this orchestration file breaks all branch coverage.

## Test signals
The expected signal is consistent daily coverage across normal tests, s390x emulation, stress, race, ASAN, and MSAN for the resolved release SHA.
