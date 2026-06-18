# sources/storage-engines/pebble/.github/workflows/nightlies-26.1.yaml

## Purpose
This workflow schedules daily nightly testing for branch `crl-release-26.1`.

## Important APIs, types, and functions
It defines `BRANCH=crl-release-26.1`, resolves `origin/$BRANCH`, and invokes reusable `tests`, `s390x`, `stress`, and `instrumented` workflows with Go 1.25.

## Control flow
On schedule or manual dispatch, the resolver job checks out full history and emits branch/SHA outputs. The four downstream jobs all depend on this resolver and run against the same resolved commit.

## State and persistence behavior
Only workflow outputs and optional failure issues persist. The code checkout itself is not modified by this orchestration file.

## Dependencies and integration points
It integrates the 26.1 release line with the shared nightly workflow suite. It assumes reusable workflows continue to support Go-version and failure-issue inputs.

## Risks and edge cases
Branch resolution is a single point of failure. A mismatch between release branch Go requirements and hardcoded Go 1.25 would cause noisy failures or missed coverage.

## Test signals
Daily success across standard, architecture, stress, and sanitizer/race jobs is the release health signal.
