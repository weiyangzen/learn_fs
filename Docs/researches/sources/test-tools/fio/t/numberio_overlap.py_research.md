# sources/test-tools/fio/t/numberio_overlap.py

## Purpose
Regression harness for fio verify `numberio` handling when writes overlap because `io_size > size`, random maps are disabled, mixed modes revisit offsets, real file size is smaller than configured size, or multiple files share the job.

## Important APIs, Types, and Functions
`OfflineOverlapVerifyTest` runs separate write and `verify_only` phases and checks both JSON outputs. `OnlineOverlapVerifyTest` runs a single `--do_verify=1` job. Both build fio arguments dynamically, support multi-file `--filename` strings, parse JSON with leading text stripped, and validate `verify_errors`, write byte counts, and verify read byte counts where exact expectations are meaningful. `TEST_LIST` encodes 13 offline/online scenarios.

## Control Flow
`main()` resolves fio, optionally probes requirements, fills every test's target filename, selects async and sync engines by platform or `--ioengines`, deep-copies the test matrix for each engine, and calls `run_fio_tests()`. Offline tests run a write phase with `--do_verify=0` followed by a verify phase with `--verify_only=1 --verify_write_sequence=1`. Online tests run write and verify in one job.

## State and Persistence Behavior
Artifacts are written under `numberio-overlap-test-<timestamp>/<engine>/<test_id>`. Test data is written to the user-selected `--file` path, and multi-file cases append `.0`, `.1`, etc. Some tests pre-create/truncate files to force `real_file_size < size`.

## Dependencies and Integration Points
Depends on fio verify internals, JSON output, platform ioengines, `fiotestlib`, and `fiotestcommon.Requirements`. It specifically targets overlap-risk and rb-tree `io_hist` paths in fio verification.

## Risks
The script is destructive to the target file path. Random `norandommap` cases intentionally skip exact read-byte assertions because coverage is probabilistic. Mixed read/write modes skip byte assertions because read counts combine workload reads and verify reads. Platform engine defaults can make results dependent on local async engine support.

## Test Signals
Passing tests indicate overlapping writes complete to `io_size`, verify reads check only the latest numberio once per block in deterministic cases, no verify errors occur in overlap scenarios, early rb-tree initialization works for short real files, and multi-file overlap accounting works.
