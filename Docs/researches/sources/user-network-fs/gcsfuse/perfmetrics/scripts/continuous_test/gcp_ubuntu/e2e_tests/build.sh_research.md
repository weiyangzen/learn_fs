# sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/e2e_tests/build.sh

## Purpose

Kokoro entrypoint for building an installed gcsfuse package at the selected commit and running regional or zonal integration tests.

## Important APIs, Types, and Functions

Consumes `KOKORO_ARTIFACTS_DIR`, `KOKORO_BUILD_INITIATOR`, and optional `RUN_TESTS_WITH_ZONAL_BUCKET`. Calls `build_and_install_gcsfuse.sh` and `tools/integration_tests/improved_run_e2e_tests.sh`.

## Control Flow

Rejects positional arguments, enters the checkout, selects branch/commit using scheduler/manual logic, builds and installs gcsfuse while capturing build logs, checks out the selected commit, then runs `improved_run_e2e_tests.sh --test-installed-package` with optional `--zonal`.

## State and Persistence Behavior

Installs a system gcsfuse package and changes the git worktree to the selected commit. Failure logs are collected by Kokoro configs.

## Dependencies and Integration Points

Depends on Kokoro checkout layout, git history, package build script, installed package behavior, and the integration test runner. Referenced by master, release, and zonal e2e configs.

## Risks and Edge Cases

Any positional arg fails the script. Scheduler commit selection requires sufficient git history. Non-`true` values of `RUN_TESTS_WITH_ZONAL_BUCKET` warn and run regional tests rather than failing fast.

## Test Signals

Successful build/install, checkout to intended commit, runner invocation in regional or zonal mode, and collected failed integration/proxy logs.
