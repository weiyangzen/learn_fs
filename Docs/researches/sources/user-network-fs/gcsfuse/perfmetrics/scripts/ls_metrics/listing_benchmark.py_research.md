<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/ls_metrics/listing_benchmark.py -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/ls_metrics/listing_benchmark.py

## Purpose
Benchmarks recursive listing or another supplied command against a GCSFuse-mounted bucket and a local persistent-disk mirror, then exports comparable latency summaries to Google Sheets and optionally BigQuery.

## Important APIs, Types, And Functions
`_count_number_of_files_and_folders`, `_get_values_to_export`, `_parse_results`, `_record_time_of_operation`, `_perform_testing`, `_create_directory_structure`, `_list_directory`, `_compare_directory_structure`, `_export_to_gsheet`, `_export_to_bigquery`, and CLI parsing. Global `RUN_1M_TEST` controls whether the 1M-file case is skipped.

## Control Flow
Main parses JSON into `Directory` protobuf, checks whether GCS already has the requested tree, deletes/recreates persistent-disk and temporary generation directories, optionally clears the bucket, generates files locally and in GCS, mounts with supplied flags, times the command for each top-level test folder on both media, computes statistics, uploads selected outputs, cleans the local tree, and unmounts.

## State And Persistence Behavior
Creates/removes `persistent_disk`, `generate_files.TEMPORARY_DIRECTORY`, the mount directory, and bucket contents when the structure mismatches. It mutates global `RUN_1M_TEST` from CLI state and uses process CWD changes for Sheets credentials.

## Dependencies
Uses generated `directory_pb2`, `google.protobuf.json_format.ParseDict`, `generate_files`, `gcloud storage`, `gcsfuse`, `numpy`, Sheets helpers, BigQuery helpers, and shared mount/dependency utilities.

## Integration Points
Driven by `run_ls_benchmark.sh`, with configs `config.json` and `config-hns.json`. Its BigQuery upload targets the experiments table constants and prepends mount type to row payloads.

## Risks And Edge Cases
Heavy use of `shell=True`, recursive deletion of bucket and local paths, and unchecked command strings makes input trust important. The 1M-file skip is name-based. Statistics require enough samples for stdev, and generated protobuf version compatibility is handled externally by the wrapper.

## Test Signals
Companion tests cover recursive file/folder counting, metrics formatting, timing, tree creation, structure comparison, export calls, and 1M-file skip behavior with subprocesses mocked.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/ls_metrics/listing_benchmark.py -->
