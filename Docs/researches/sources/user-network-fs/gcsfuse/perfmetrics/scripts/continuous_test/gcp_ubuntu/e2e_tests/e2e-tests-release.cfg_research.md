# sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/e2e_tests/e2e-tests-release.cfg

## Purpose

Kokoro config for standard release-job gcsfuse e2e tests.

## Important APIs, Types, and Functions

Collects gcsfuse failed integration logs, proxy-server failed integration logs, and Sponge logs. Uses shared `e2e_tests/build.sh`.

## Control Flow

Kokoro runs the shared build script. With no zonal env var, the script builds/installs the selected checkout and runs regional e2e tests.

## State and Persistence Behavior

Persists release failure artifacts and Sponge logs. Package installation and checkout are delegated to the build script.

## Dependencies and Integration Points

Integrates with release Kokoro context, shared e2e build script, integration runner, and failure log naming.

## Risks and Edge Cases

Master and release configs are structurally identical; release-specific behavior must come from Kokoro job context. Any release-only environment or retention needs must be added explicitly.

## Test Signals

Release Kokoro logs with selected branch/commit, installed-package e2e execution, and collected gcsfuse/proxy/Sponge logs on failure.
