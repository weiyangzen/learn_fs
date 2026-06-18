# sources/storage-engines/pebble/.github/workflows/nightlies-25.2.yaml

## Purpose
This workflow schedules daily nightly testing for branch `crl-release-25.2`.

## Important APIs, types, and functions
It runs on a daily cron at 10:30 UTC and manual dispatch. A `resolve-sha` job checks out history and records `branch` and `sha` outputs. Downstream jobs call reusable `tests.yaml`, `s390x.yaml`, `stress.yaml`, and `instrumented.yaml` with Go 1.23.

## Control flow
The resolver fetches the repository, runs `git rev-parse origin/$BRANCH`, and exposes both branch and SHA. The reusable test jobs then run against that exact SHA and use the branch name for issue filing.

## State and persistence behavior
Workflow state is limited to job outputs and any failure issues/comments created by downstream reusable workflows.

## Dependencies and integration points
It integrates release branch maintenance with the shared nightly test suite and assumes `origin/crl-release-25.2` exists.

## Risks and edge cases
If the branch is removed or renamed, SHA resolution fails and no downstream tests run. Go 1.23 must remain available on setup-go. All child workflows must accept the same input contract.

## Test signals
The signal is a daily pass/fail matrix for normal, s390x, stress, and instrumented coverage on the release branch.
