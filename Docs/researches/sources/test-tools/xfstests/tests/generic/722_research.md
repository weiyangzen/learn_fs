# sources/test-tools/xfstests/tests/generic/722

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/722`. Test exchangerange with the fsync flag flushes everything to disk before the call returns. It is registered with `_begin_fstest auto quick fiexchange`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 56 source line(s).
- Harness registration: `_begin_fstest auto quick fiexchange`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/reflink`.
- Capability and skip gates: `_require_test_program "punch-alternating"`, `_require_xfs_io_command exchangerange`, `_require_scratch`, `_require_scratch_shutdown`, `_require_metadata_journaling`.
- Local shell functions: none visible.
- External `$here/src` helpers: `$here/src/punch-alternating $SCRATCH_MNT/a`, `$here/src/punch-alternating $SCRATCH_MNT/b`.
- Notable variables and constants:
- `old_a=$(md5sum $SCRATCH_MNT/a | awk '{print $1}')`
- `old_b=$(md5sum $SCRATCH_MNT/b | awk '{print $1}')`
- `new_a=$(md5sum $SCRATCH_MNT/a | awk '{print $1}')`
- `new_b=$(md5sum $SCRATCH_MNT/b | awk '{print $1}')`

## Control Flow

- Capability gating runs first through `_require_test_program "punch-alternating"`, `_require_xfs_io_command exchangerange`, `_require_scratch`, `_require_scratch_shutdown`, `_require_metadata_journaling`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 33: echo "md5 a: $old_a md5 b: $old_b" >> $seqres.full`
- `line 38: echo swap >> $seqres.full`
- `line 45: echo "md5 a: $new_a md5 b: $new_b" >> $seqres.full`
- `line 54: echo Silence is golden`
- Key operational lines include:
- `line 18: _require_xfs_io_command exchangerange`
- `line 20: _require_scratch_shutdown`
- `line 23: _scratch_mkfs >> $seqres.full`
- `line 24: _scratch_mount`
- `line 31: old_a=$(md5sum $SCRATCH_MNT/a | awk '{print $1}')`
- `line 32: old_b=$(md5sum $SCRATCH_MNT/b | awk '{print $1}')`
- `line 39: $XFS_IO_PROG -c "exchangerange -f $SCRATCH_MNT/a" $SCRATCH_MNT/b`
- `line 40: _scratch_shutdown`
- `line 41: _scratch_cycle_mount`
- `line 43: new_a=$(md5sum $SCRATCH_MNT/a | awk '{print $1}')`
- `line 44: new_b=$(md5sum $SCRATCH_MNT/b | awk '{print $1}')`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick fiexchange`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/reflink`), and the golden-output file `sources/test-tools/xfstests/tests/generic/722.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_test_program "punch-alternating"`, `_require_xfs_io_command exchangerange`, `_require_scratch`, `_require_scratch_shutdown`, `_require_metadata_journaling`.

## Risks and Edge Cases

- Failure-injection paths can leave mounts or synthetic device tables behind if cleanup is interrupted.
- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 722; Silence is golden'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, post-remount or failure-injection persistence checks. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
