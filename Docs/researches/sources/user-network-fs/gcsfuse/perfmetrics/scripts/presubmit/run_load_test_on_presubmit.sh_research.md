<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/presubmit/run_load_test_on_presubmit.sh -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/presubmit/run_load_test_on_presubmit.sh

## Purpose
Runs the presubmit fio workload and appends parsed results to `result.txt`.

## Important APIs, Types, And Functions
Shell entry point with positional arguments and local helper functions where defined.

## Control Flow
Calls fio with `presubmit_perf_test.fio`, JSON output, and latency percentiles, then invokes `presubmit/fetch_results.py`.

## State And Persistence Behavior
Creates `output.json` and appends `result.txt` through the Python parser.

## Dependencies
Depends on fio and the repo-relative presubmit scripts.

## Integration Points
Part of the GCSFuse perfmetrics automation under the same source tree.

## Risks And Edge Cases
No cleanup or mount handling; it assumes caller has mounted the correct `gcs` path.

## Test Signals
No direct tests in this subset unless invoked by a higher-level Kokoro or wrapper job.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/presubmit/run_load_test_on_presubmit.sh -->
