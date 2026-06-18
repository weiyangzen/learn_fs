<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/presubmit/print_results.py -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/presubmit/print_results.py

## Purpose
Formats presubmit benchmark comparison data from `result.txt` as a PrettyTable comparing master and PR branches.

## Important APIs, Types, And Functions
Reads all lines from `result.txt`; constants `DATA_DIMENSION=5` and `DATA_SET_SPLIT_INDEX=15` define expected layout.

## Control Flow
Builds a table with branch, file size, and four bandwidth columns, then loops over three file-size groups for master and PR data.

## State And Persistence Behavior
Reads `result.txt` and prints the table to stdout.

## Dependencies
Requires `prettytable` and the exact output order produced by two `fetch_results.py` runs.

## Integration Points
Called by the PR perf Kokoro build after master and PR fio runs.

## Risks And Edge Cases
No length checks; malformed or missing result data causes index errors or misleading rows.

## Test Signals
No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/presubmit/print_results.py -->
