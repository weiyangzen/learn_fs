<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/pynfs/baseline/current-v4.0.json -->
# sources/test-tools/kdevops/workflows/pynfs/baseline/current-v4.0.json

## Purpose
This file is a stored pynfs NFSv4.0 baseline result in JSON form. It is not executable logic; it captures the expected result envelope for an `all` pynfs run so kdevops can compare future test output against a known baseline. The top-level schema is junit-like: `name`, `tests`, `failures`, `errors`, `skipped`, `time`, `timestamp`, and a `testcase` array.

## Important Data Shape
The baseline records `tests: 679`, `failures: 1`, `errors: 0`, `skipped: 98`, and a total runtime near 1782.75 seconds with timestamp `2023-03-20 16:13:01.857565`. Each testcase object carries at least `classname`, `name`, and `time`; skipped cases include `skipped: 1`, and failed cases include a nested `failure` object with `err` and `message`.

The only recorded failure is `st_lock.testOpenUpgradeLock`, where `OP_LOCK` returned `NFS4ERR_BAD_SEQID` instead of `NFS4_OK`. High-volume classes include `st_setattr`, `st_getattr`, `st_rename`, `st_nverify`, `st_verify`, `st_lock`, and `st_open`.

## Control Flow and Integration
The file is produced by the pynfs runner, specifically the NFSv4.0 leg in `run_pynfs.sh`, which writes `${PYNFS_DATA}/pynfs-4.0-results.json` after running `./testserver.py ... "${EXPORT_BASE}-4.0" all`. Downstream playbooks or result checkers can use this baseline to decide whether a current run differs materially from the accepted state.

## State, Persistence, and Dependencies
Persistence is the JSON artifact itself. The external dependency is the pynfs testserver output format; any schema drift in pynfs will affect consumers. Since this file stores timestamps and duration, consumers should compare semantic fields such as test names, failure messages, and skip counts rather than expecting byte-for-byte stability.

## Risks and Test Signals
The failure count is intentionally nonzero, so tooling must not treat any failure as automatically fatal without consulting the baseline. The `status_counts` inferred from the data are not explicit because passing cases omit `status`; readers must interpret missing failure/error/skipped fields as pass. The key regression signals are changes in the single `st_lock` failure, the 98 skipped tests, and the total testcase count of 679.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/pynfs/baseline/current-v4.0.json -->
