# sources/storage-engines/pebble/.github/workflows/nightlies-25.4.yaml

## Purpose
This workflow schedules daily nightly testing for branch `crl-release-25.4`.

## Important APIs, types, and functions
It uses the same resolver pattern as other release nightlies: scheduled/manual triggers, `BRANCH=crl-release-25.4`, `git rev-parse origin/$BRANCH`, and calls to `tests.yaml`, `s390x.yaml`, `stress.yaml`, and `instrumented.yaml` with Go 1.23.

## Control flow
The `resolve-sha` job produces stable branch and SHA outputs. Four reusable workflows consume the SHA and branch name, ensuring all jobs test the same release commit and file issues under the release branch label.

## State and persistence behavior
No repository state is changed. Persistent state can be created only through downstream failure issue reporting.

## Dependencies and integration points
It depends on the shared reusable workflow interface and the existence of `origin/crl-release-25.4`.

## Risks and edge cases
The cron string has a trailing space but is otherwise valid YAML text for GitHub scheduling. Go 1.23 availability and reusable workflow compatibility are required for continued release validation.

## Test signals
Nightly pass/fail across standard tests, s390x, stress, and instrumented variants is the expected release health signal.
