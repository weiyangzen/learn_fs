<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/hns_rename_folders_metrics/run_rename_benchmark.sh -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/hns_rename_folders_metrics/run_rename_benchmark.sh

## Purpose
Installs FUSE/pip and Python requirements, installs Ops Agent, fetches Sheets credentials, installs latest gcloud, and runs the HNS rename benchmark with user-supplied upload flags.

## Important APIs, Types, And Functions
Shell entry point with positional arguments and local helper functions where defined.

## Control Flow
It is a VM/Kokoro wrapper around `renaming_benchmark.py`; flat-bucket execution is currently commented out.

## State And Persistence Behavior
System package installs, Ops Agent install, credential copy from `gs://periodic-perf-tests/creds.json`, and gcloud replacement are persistent host mutations.

## Dependencies
Requires sudo apt, curl, gcloud storage access, `requirements.txt` generated from the sibling `.in`, and a config-hns JSON file.

## Integration Points
Part of the GCSFuse perfmetrics automation under the same source tree.

## Risks And Edge Cases
Risks include broad host mutation, no argument validation, commented flat path reducing comparison coverage, and reliance on relative paths.

## Test Signals
No direct tests in this subset unless invoked by a higher-level Kokoro or wrapper job.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/hns_rename_folders_metrics/run_rename_benchmark.sh -->
