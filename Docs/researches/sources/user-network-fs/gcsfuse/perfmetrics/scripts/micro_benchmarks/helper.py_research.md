<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/micro_benchmarks/helper.py -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/micro_benchmarks/helper.py

## Purpose
Shared helper for single-thread microbenchmarks: mount/unmount a bucket with GCSFuse, log throughput to BigQuery, and compare recent BigQuery bandwidth history against thresholds.

## Important APIs, Types, And Functions
`mount_bucket`, `unmount_gcs_directory`, `log_to_bigquery`, `get_last_n_days_bandwidth_entries`, and `check_and_alert_bandwidth`. Constants define the BigQuery project, dataset, and table.

## Control Flow
Mount helpers shell out to `gcsfuse` and `fusermount`. Logging computes MB/s, builds a pandas DataFrame, and loads it into BigQuery. Validation queries the last N days for a workload type and exits with status 1 if the historical average is below threshold.

## State And Persistence Behavior
Creates mount directories, mounts FUSE filesystems, writes BigQuery rows, and can terminate the process on alert failure.

## Dependencies
Uses `google-cloud-bigquery`, `pandas`, `subprocess`, and local GCSFuse installation.

## Integration Points
Imported by `read_single_thread.py` and `write_single_thread.py`; orchestrated by `run_microbenchmark.sh`.

## Risks And Edge Cases
The BigQuery query interpolates `workload_type` into SQL, threshold logic compares historical average rather than current run, and mount flags are passed through a shell command string.

## Test Signals
Unit tests mock subprocess and BigQuery clients, covering success/failure branches for mounts, unmounts, and BigQuery load exceptions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/micro_benchmarks/helper.py -->
