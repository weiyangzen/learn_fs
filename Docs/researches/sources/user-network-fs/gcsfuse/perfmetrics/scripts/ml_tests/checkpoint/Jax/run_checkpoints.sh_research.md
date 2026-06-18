<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/ml_tests/checkpoint/Jax/run_checkpoints.sh -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/ml_tests/checkpoint/Jax/run_checkpoints.sh

## Purpose
Kokoro-style driver for JAX checkpoint tests across flat, HNS, and zonal buckets.

## Important APIs, Types, And Functions
Defines `mount_gcsfuse_and_run_test`, installs Go/gcloud/Python dependencies, builds GCSFuse, creates a venv, and launches three background checkpoint workloads.

## Control Flow
Installs Go, upgrades gcloud/Python, builds `gcsfuse`, installs JAX requirements, determines zone and architecture, clears each target bucket, mounts with streaming writes and trace logs, runs `emulated_checkpoints.py`, waits for all three background jobs, and fails if any job fails.

## State And Persistence Behavior
Deletes objects from test buckets, writes logs under `KOKORO_ARTIFACTS_DIR/gcsfuse_logs`, creates mount points under `$HOME/gcs`, creates a venv, and runs background processes.

## Dependencies
Requires Kokoro env vars, Go, gcloud alpha storage, Python 3.11, JAX dependencies, and Google metadata server.

## Integration Points
Invoked from presubmit build logic when checkpoint label is present.

## Risks And Edge Cases
No explicit unmount in the function, bucket cleanup is broad, and parallel jobs share the same built source tree. Architecture is taken from `dpkg --print-architecture` for Go tarball naming.

## Test Signals
No local tests; success is process exit status from the three checkpoint workloads.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/ml_tests/checkpoint/Jax/run_checkpoints.sh -->
