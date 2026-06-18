<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/pynfs/baseline/current-v4.1.json -->
# sources/test-tools/kdevops/workflows/pynfs/baseline/current-v4.1.json

## Purpose
This file is the stored pynfs NFSv4.1 baseline result. Like the v4.0 baseline, it is a data artifact rather than code, and it anchors expected behavior for a kdevops pynfs run against an NFSv4.1 export.

## Important Data Shape
The top-level object contains `name: all`, `tests: 262`, `failures: 0`, `errors: 0`, `skipped: 91`, `time: 546.1761648654938`, `timestamp: 2023-03-20 16:22:10.506308`, and an array of 262 testcase objects. Testcases include `classname`, `name`, and `time`; skipped cases use `skipped: 1`. Passing cases do not carry an explicit status field.

Prominent classes include `st_rename`, `st_create_session`, `st_exchange_id`, `st_flex`, `st_sequence`, `st_reboot`, `st_xattr`, `st_current_stateid`, and `st_delegation`. All `st_flex`, `st_reboot`, `st_xattr`, and `st_delegation` cases visible in the class summaries are skipped, so the baseline includes substantial unsupported or intentionally omitted coverage.

## Control Flow and Integration
`run_pynfs.sh` runs the NFSv4.1 leg by changing into `${PYNFS_DATA}/nfs4.1` and invoking `testserver.py` with JSON output at `${PYNFS_DATA}/pynfs-4.1-results.json`. The flags for this leg are `all deleg xattr`, making the baseline sensitive to delegation and extended attribute coverage even when many of those tests are skipped.

## State, Persistence, and Dependencies
The file persists a historical expected result for comparison. It depends on pynfs JSON formatting and test class naming. Because runtime fields are environmental, robust consumers should focus on testcase identity, skip/failure/error fields, and aggregate counts.

## Risks and Test Signals
This baseline expects no failures or errors but many skips. A new failure is a strong regression signal; a skipped-to-passed transition may be improvement but still changes baseline accounting. The 262 testcase count and 91 skipped tests are the key checks. Since this is v4.1-specific, consumers must not compare it directly with the v4.0 baseline, which has a different testcase universe and one accepted failure.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/pynfs/baseline/current-v4.1.json -->
