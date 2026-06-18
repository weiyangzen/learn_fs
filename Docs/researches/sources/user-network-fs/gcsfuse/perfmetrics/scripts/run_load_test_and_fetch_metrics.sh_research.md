<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/run_load_test_and_fetch_metrics.sh -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/run_load_test_and_fetch_metrics.sh

## Purpose
Runs a fio load test against a mounted GCSFuse bucket, unmounts it, then fetches and uploads fio metrics.

## Important APIs, Types, And Functions
Shell entry point with positional arguments and local helper functions where defined.

## Control Flow
It installs pip/fio, mounts a passed bucket under `gcs`, records start/end epoch times, runs `seq_rand_read_write.fio` with JSON output, unmounts, installs Python requirements, fetches credentials, and invokes `fetch_and_upload_metrics.py`.

## State And Persistence Behavior
Creates `gcs`, produces `fio-output${EXPERIMENT_NUMBER}.json`, installs user packages, and writes credentials under `gsheet`.

## Dependencies
Depends on Kokoro artifact layout, fio installer, gcsfuse binary, job file, pip requirements, gcloud storage, and spreadsheet id.

## Integration Points
Part of the GCSFuse perfmetrics automation under the same source tree.

## Risks And Edge Cases
Mount flags and bucket are unquoted; if fio fails, set -e prevents unmount cleanup; environment variable `EXPERIMENT_NUMBER` is assumed.

## Test Signals
No direct tests in this subset unless invoked by a higher-level Kokoro or wrapper job.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/run_load_test_and_fetch_metrics.sh -->
