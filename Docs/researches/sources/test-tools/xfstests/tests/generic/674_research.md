# sources/test-tools/xfstests/tests/generic/674

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/674`. Functional test for dropping suid and sgid bits as part of a deduplication. It is registered with `_begin_fstest auto clone quick perms dedupe`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 116 source line(s).
- Harness registration: `_begin_fstest auto clone quick perms dedupe`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/reflink`.
- Capability and skip gates: `_require_user`, `_require_scratch_dedupe`, `_require_xfs_io_command dedupe`, `_require_congruent_file_oplen $SCRATCH_MNT 1048576`.
- Local shell functions: `setup_testfile`, `commit_and_check`.
- External `$here/src` helpers: none visible.

## Control Flow

- Capability gating runs first through `_require_user`, `_require_scratch_dedupe`, `_require_xfs_io_command dedupe`, `_require_congruent_file_oplen $SCRATCH_MNT 1048576`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 56: echo "before: $before_freesp; after: $after_freesp" >> $seqres.full`
- `line 58: echo "expected more free space after dedupe"`
- `line 62: echo`
- `line 67: echo "Test 1 - qa_user, non-exec file"`
- `line 73: echo "Test 2 - qa_user, group-exec file"`
- `line 79: echo "Test 3 - qa_user, user-exec file"`
- `line 85: echo "Test 4 - qa_user, all-exec file"`
- `line 91: echo "Test 5 - root, non-exec file"`
- Key operational lines include:
- `line 10: _begin_fstest auto clone quick perms dedupe`
- `line 19: _require_scratch_dedupe`
- `line 20: _require_xfs_io_command dedupe`
- `line 22: _scratch_mkfs >> $seqres.full`
- `line 23: _scratch_mount`
- `line 32: _scratch_sync`
- `line 38: md5sum $SCRATCH_MNT/a | _filter_scratch`
- `line 39: stat -c '%a %A %n' $SCRATCH_MNT/a | _filter_scratch`
- `line 43: local cmd="$XFS_IO_PROG -c 'dedupe $SCRATCH_MNT/b 0 0 1m' $SCRATCH_MNT/a"`
- `line 50: _scratch_cycle_mount`
- `line 51: md5sum $SCRATCH_MNT/a | _filter_scratch`
- `line 52: stat -c '%a %A %n' $SCRATCH_MNT/a | _filter_scratch`
- `line 58: echo "expected more free space after dedupe"`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto clone quick perms dedupe`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/reflink`), and the golden-output file `sources/test-tools/xfstests/tests/generic/674.out` (49 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_user`, `_require_scratch_dedupe`, `_require_xfs_io_command dedupe`, `_require_congruent_file_oplen $SCRATCH_MNT 1048576`.

## Risks and Edge Cases

- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 49 line(s); its first visible signals are: 'QA output created by 674; Test 1 - qa_user, non-exec file; 310f146ce52077fcd3308dcbe7632bb2  SCRATCH_MNT/a; 6666 -rwSrwSrw- SCRATCH_MNT/a; 310f146ce52077fcd3308dcbe7632bb2  SCRATCH_MNT/a'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, xfstests output filters, post-remount or failure-injection persistence checks. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
