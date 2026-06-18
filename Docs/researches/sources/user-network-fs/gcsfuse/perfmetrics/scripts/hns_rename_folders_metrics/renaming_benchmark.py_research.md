<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/hns_rename_folders_metrics/renaming_benchmark.py -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/hns_rename_folders_metrics/renaming_benchmark.py

## Purpose
Runs the HNS-vs-flat folder rename benchmark. It validates a generated folder configuration, mounts the bucket with the correct GCSFuse HNS or flat flags, times alternating `mv` operations for simple and nested folders, computes latency statistics, waits for Cloud Monitoring lag, fetches VM metrics, and optionally uploads both result families to Google Sheets.

## Important APIs, Types, And Functions
`_run_rename_benchmark`, `_perform_testing`, `_record_time_of_operation`, `_record_time_for_folder_rename`, `_parse_results`, `_compute_metrics_from_time_of_operation`, `_get_values_to_export`, `_extract_vm_metrics`, `_upload_to_gsheet`, and CLI parsing. Constants select sheet tabs and the monitoring instance hostname.

## Control Flow
The CLI requires a config path and `hns` or `flat`. `_run_rename_benchmark` loads JSON, delegates schema/existence checks to `generate_folders_and_files`, mounts using `mount_gcs_bucket`, records rename timings per folder, summarizes latency rows, sleeps 360 seconds for monitoring data availability, fetches VM metric rows for the same time ranges, then either prints or uploads.

## State And Persistence Behavior
Creates `/tmp/config.yml`, creates and removes a local mount directory named after the bucket through the mount helper, mutates benchmark folders by renaming them back and forth, changes process CWD around Google Sheets credential lookup, and sleeps before reading Cloud Monitoring data.

## Dependencies
Uses `numpy`, `statistics`, `gcsfuse`, `gcloud`, Google Sheets helper, VM metrics helper, `generate_folders_and_files`, and the shared mount/dependency utilities.

## Integration Points
Called by `run_rename_benchmark.sh` in VM/Kokoro style jobs and depends on prior population of config-declared folders. Its output rows align with `rename_metrics_*` and `vm_metrics_*` worksheets.

## Risks And Edge Cases
Most shell calls interpolate folder names with `shell=True`; unusual names can break commands. `stat.stdev` fails for one sample, mount errors drop into an interactive shell rather than raising, and the fixed 360 second sleep dominates runtime. CWD changes make credential path assumptions fragile.

## Test Signals
Unit coverage exercises file counting, rename command sequencing, mount flag selection, metric computation/export row shape, upload error handling, and high-level `_run_rename_benchmark` branches with mocks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/hns_rename_folders_metrics/renaming_benchmark.py -->
