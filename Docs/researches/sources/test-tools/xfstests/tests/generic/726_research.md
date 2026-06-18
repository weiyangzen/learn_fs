# sources/test-tools/xfstests/tests/generic/726

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/726`. Functional test for dropping suid and sgid bits as part of an atomic file commit. It is registered with `_begin_fstest auto fiexchange quick`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 113 source line(s).
- Harness registration: `_begin_fstest auto fiexchange quick`.
- Imported common libraries: `./common/preamble`, `./common/filter`.
- Capability and skip gates: `_require_user`, `_require_xfs_io_command exchangerange`, `_require_xfs_io_command startupdate`, `_require_scratch`, `_require_congruent_file_oplen $SCRATCH_MNT 1048576`.
- Local shell functions: `setup_testfile`, `commit_and_check`.
- External `$here/src` helpers: none visible.

## Control Flow

- Capability gating runs first through `_require_user`, `_require_xfs_io_command exchangerange`, `_require_xfs_io_command startupdate`, `_require_scratch`, `_require_congruent_file_oplen $SCRATCH_MNT 1048576`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 59: echo`
- `line 64: echo "Test 1 - qa_user, non-exec file"`
- `line 70: echo "Test 2 - qa_user, group-exec file"`
- `line 76: echo "Test 3 - qa_user, user-exec file"`
- `line 82: echo "Test 4 - qa_user, all-exec file"`
- `line 88: echo "Test 5 - root, non-exec file"`
- `line 94: echo "Test 6 - root, group-exec file"`
- `line 100: echo "Test 7 - root, user-exec file"`
- Key operational lines include:
- `line 26: _require_xfs_io_command exchangerange`
- `line 27: _require_xfs_io_command startupdate`
- `line 30: _scratch_mkfs >> $seqres.full`
- `line 31: _scratch_mount`
- `line 38: _scratch_sync`
- `line 44: md5sum $SCRATCH_MNT/a | _filter_scratch`
- `line 45: stat -c '%a %A %n' $SCRATCH_MNT/a | _filter_scratch`
- `line 47: local cmd="$XFS_IO_PROG -c 'startupdate' -c 'pwrite -S 0x57 0 1m' -c 'commitupdate' $SCRATCH_MNT/a"`
- `line 54: _scratch_cycle_mount`
- `line 55: md5sum $SCRATCH_MNT/a | _filter_scratch`
- `line 56: stat -c '%a %A %n' $SCRATCH_MNT/a | _filter_scratch`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto fiexchange quick`, common helper libraries (`./common/preamble`, `./common/filter`), and the golden-output file `sources/test-tools/xfstests/tests/generic/726.out` (49 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_user`, `_require_xfs_io_command exchangerange`, `_require_xfs_io_command startupdate`, `_require_scratch`, `_require_congruent_file_oplen $SCRATCH_MNT 1048576`.

## Risks and Edge Cases

- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 49 line(s); its first visible signals are: 'QA output created by 726; Test 1 - qa_user, non-exec file; 310f146ce52077fcd3308dcbe7632bb2  SCRATCH_MNT/a; 6666 -rwSrwSrw- SCRATCH_MNT/a; 3784de23efab7a2074c9ec66901e39e5  SCRATCH_MNT/a'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, xfstests output filters, post-remount or failure-injection persistence checks. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
