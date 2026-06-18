# sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/e2e_tests/e2e-tests-master.cfg

## Purpose

Kokoro config for standard master-branch gcsfuse e2e tests.

## Important APIs, Types, and Functions

Collects gcsfuse failed integration logs, proxy-server failed integration logs, and Sponge logs. Uses shared `e2e_tests/build.sh`.

## Control Flow

Kokoro invokes the build script without zonal env vars, so the script defaults to regional installed-package e2e tests.

## State and Persistence Behavior

Persists failure diagnostics and Sponge logs. Runtime state is delegated to the shared build script.

## Dependencies and Integration Points

Depends on Kokoro artifact collection, shared build script regional default, and integration/proxy failure log naming.

## Risks and Edge Cases

Renamed logs or changed output paths reduce diagnostics. Regional/zonal behavior is implicit through absence of an env var.

## Test Signals

Logs stating regional tests are running by default, e2e runner result, and uploaded gcsfuse/proxy failure logs when applicable.
