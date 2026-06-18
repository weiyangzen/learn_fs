# sources/test-tools/xfstests/tests/generic/727

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/727`. Functional test for dropping capability bits as part of an atomic file commit. It is registered with `_begin_fstest auto fiexchange quick`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 83 source line(s).
- Harness registration: `_begin_fstest auto fiexchange quick`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/attr`.
- Capability and skip gates: `_require_user`, `_require_command "$GETCAP_PROG" getcap`, `_require_command "$SETCAP_PROG" setcap`, `_require_xfs_io_command exchangerange`, `_require_xfs_io_command startupdate`, `_require_scratch`, `_require_attrs security`, `_require_congruent_file_oplen $SCRATCH_MNT 1048576`.
- Local shell functions: `setup_testfile`, `commit_and_check`.
- External `$here/src` helpers: none visible.

## Control Flow

- Capability gating runs first through `_require_user`, `_require_command "$GETCAP_PROG" getcap`, `_require_command "$SETCAP_PROG" setcap`, `_require_xfs_io_command exchangerange`, `_require_xfs_io_command startupdate`, plus 3 more.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 68: echo`
- `line 72: echo "Test 1 - qa_user"`
- `line 77: echo "Test 2 - root"`
- Key operational lines include:
- `line 29: _require_xfs_io_command exchangerange`
- `line 30: _require_xfs_io_command startupdate`
- `line 34: _scratch_mkfs >> $seqres.full`
- `line 35: _scratch_mount`
- `line 45: _scratch_sync`
- `line 51: md5sum $SCRATCH_MNT/a | _filter_scratch`
- `line 52: stat -c '%a %A %n' $SCRATCH_MNT/a | _filter_scratch`
- `line 55: local cmd="$XFS_IO_PROG -c 'startupdate' -c 'pwrite -S 0x57 0 1m' -c 'commitupdate' $SCRATCH_MNT/a"`
- `line 62: _scratch_cycle_mount`
- `line 63: md5sum $SCRATCH_MNT/a | _filter_scratch`
- `line 64: stat -c '%a %A %n' $SCRATCH_MNT/a | _filter_scratch`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Extended attributes are part of the persistent state being created, replayed, or verified. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto fiexchange quick`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/attr`), and the golden-output file `sources/test-tools/xfstests/tests/generic/727.out` (17 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_user`, `_require_command "$GETCAP_PROG" getcap`, `_require_command "$SETCAP_PROG" setcap`, `_require_xfs_io_command exchangerange`, `_require_xfs_io_command startupdate`, `_require_scratch`, `_require_attrs security`, `_require_congruent_file_oplen $SCRATCH_MNT 1048576`.

## Risks and Edge Cases

- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 17 line(s); its first visible signals are: 'QA output created by 727; Test 1 - qa_user; 310f146ce52077fcd3308dcbe7632bb2  SCRATCH_MNT/a; 666 -rw-rw-rw- SCRATCH_MNT/a; SCRATCH_MNT/a cap_setgid,cap_setuid=ep'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, xfstests output filters, post-remount or failure-injection persistence checks. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
