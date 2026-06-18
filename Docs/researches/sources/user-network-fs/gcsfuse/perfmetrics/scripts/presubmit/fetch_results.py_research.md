<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/presubmit/fetch_results.py -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/presubmit/fetch_results.py

## Purpose
Extracts selected fio metrics from a presubmit fio JSON output and appends compact values to `result.txt`.

## Important APIs, Types, And Functions
CLI expects one fio JSON path, imports `FioMetrics` from `perfmetrics/scripts/fio/fio_metrics.py`, and writes size/read-write bandwidth lines.

## Control Flow
Loads fio metrics, iterates returned workload records, writes file size once for read rows, then writes bandwidth in MiB/s for each operation.

## State And Persistence Behavior
Appends to `result.txt` in the current working directory.

## Dependencies
Depends on fio metrics parser and a specific current-directory layout where `./perfmetrics/scripts/` is importable.

## Integration Points
Called by `presubmit/run_load_test_on_presubmit.sh`; consumed by `print_results.py` after master and PR runs append their data.

## Risks And Edge Cases
Hard-coded append order and line counts; no context manager; assumes `rw == read` identifies the start of each file-size group.

## Test Signals
No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/presubmit/fetch_results.py -->
