# sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/e2e_tests/e2e-tests-master-zb.cfg

## Purpose

Kokoro config for master-branch e2e tests against zonal buckets.

## Important APIs, Types, and Functions

Collects failed integration logs, Sponge logs, and `proxy*` artifacts. Sets `RUN_TESTS_WITH_ZONAL_BUCKET=true` and uses shared `e2e_tests/build.sh`.

## Control Flow

Kokoro injects the zonal env var; the build script detects exact `true` and runs the integration runner with `--zonal`.

## State and Persistence Behavior

Persists zonal failure/proxy artifacts and Sponge logs. Runtime package install and checkout happen in the build script.

## Dependencies and Integration Points

Depends on Kokoro env var injection, artifact collection, shared build script, and integration runner zonal mode.

## Risks and Edge Cases

Exact env var spelling/value controls zonal behavior. Broad `proxy*` collection may include unexpected files; diagnostics differ slightly from non-zonal configs.

## Test Signals

Logs showing zonal tests, runner invocation with `--zonal`, and collected zonal failure/proxy artifacts.
