# sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/e2e_tests/checkpoint-tests.cfg

## Purpose

Kokoro configuration for gcsfuse ML checkpoint tests.

## Important APIs, Types, and Functions

Collects `gcsfuse_logs/*` and Sponge logs, strips `github/gcsfuse/perfmetrics/scripts`, and sets `build_file` to `gcsfuse/perfmetrics/scripts/ml_tests/checkpoint/Jax/run_checkpoints.sh`.

## Control Flow

Kokoro runs the checkpoint script and collects matching artifacts. Workload logic lives in `run_checkpoints.sh`.

## State and Persistence Behavior

Controls persistence of checkpoint logs and Sponge logs only.

## Dependencies and Integration Points

Depends on Kokoro artifact handling, the ML checkpoint script path, and `gcsfuse_logs` output naming.

## Risks and Edge Cases

Moved or renamed checkpoint logs will not be collected. No explicit timeout is set here. Build file path must stay synchronized with the ML test directory.

## Test Signals

Kokoro invocation of `run_checkpoints.sh`, uploaded `gcsfuse_logs/*`, and Sponge logs on failure.
