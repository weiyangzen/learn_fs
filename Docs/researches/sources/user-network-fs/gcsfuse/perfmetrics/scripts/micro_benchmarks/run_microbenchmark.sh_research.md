<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/micro_benchmarks/run_microbenchmark.sh -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/micro_benchmarks/run_microbenchmark.sh

## Purpose
Builds and installs the current GCSFuse checkout, prepares a Python venv, then runs the single-thread read and write microbenchmarks.

## Important APIs, Types, And Functions
Shell entry point with positional arguments and local helper functions where defined.

## Control Flow
Installs base packages, changes to `$HOME/github/gcsfuse`, builds gcsfuse with the current short commit id, cleans stale mounts, installs hashed Python requirements, runs read and write benchmark scripts with log-file flags, uploads failure logs to a GCS artifact bucket, and exits nonzero if either benchmark fails.

## State And Persistence Behavior
Creates `venv`, unmounts any existing gcsfuse mounts, writes temporary log files under `/tmp`, installs gcsfuse on the host, and can copy logs to `gs://gcsfuse-kokoro-logs/...`.

## Dependencies
Depends on apt, git, Python venv, gcloud storage, `build_and_install_gcsfuse.sh`, the microbenchmark Python scripts, and bucket `single-threaded-tests`.

## Integration Points
Part of the GCSFuse perfmetrics automation under the same source tree.

## Risks And Edge Cases
Assumes a fixed checkout path and bucket name; mount cleanup scans all gcsfuse mounts on the host; failure-log upload assumes gcloud auth and artifact bucket permissions.

## Test Signals
No direct tests in this subset unless invoked by a higher-level Kokoro or wrapper job.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/micro_benchmarks/run_microbenchmark.sh -->
