<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/presubmit_test/pr_perf_test/requirements.in -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/presubmit_test/pr_perf_test/requirements.in

## Purpose
Presubmit PR perf Python dependency input.

## Important APIs, Types, And Functions
Dependency input file for pip-compile or equivalent lock generation; no executable API.

## Control Flow
Lists google-cloud, Vision/API client, and prettytable for presubmit scripts and reporting.

## State And Persistence Behavior
No runtime state; compiled `requirements.txt` is installed by sibling wrappers with `--require-hashes`.

## Dependencies
Lists google-cloud, Vision/API client, and prettytable for presubmit scripts and reporting.

## Integration Points
Installed by `build.sh` along with BigQuery requirements before optional perf tests.

## Risks And Edge Cases
Broad unpinned Google packages can drift unless compiled hash output is used.

## Test Signals
Validated indirectly when wrapper scripts install the compiled requirements and import dependent modules.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/presubmit_test/pr_perf_test/requirements.in -->
