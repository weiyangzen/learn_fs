# sources/test-tools/xfstests/tests/generic/737

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/737`. Integrity test for O_SYNC with buff-io, dio, aio-dio with sudden shutdown. Based on a testcase reported by Gao Xiang <hsiangkao@linux.alibaba.com> It is registered with `_begin_fstest auto quick shutdown aio`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 52 source line(s).
- Harness registration: `_begin_fstest auto quick shutdown aio`.
- Imported common libraries: `./common/preamble`.
- Capability and skip gates: `_require_scratch`, `_require_scratch_shutdown`, `_require_aiodio aio-dio-write-verify`.
- Local shell functions: none visible.
- External `$here/src` helpers: none visible.

## Control Flow

- Capability gating runs first through `_require_scratch`, `_require_scratch_shutdown`, `_require_aiodio aio-dio-write-verify`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 24: echo "T-1: Create a 1M file using buff-io & O_SYNC"`
- `line 26: echo "T-1: Shutdown the fs suddenly"`
- `line 28: echo "T-1: Cycle mount"`
- `line 30: echo "T-1: File contents after cycle mount"`
- `line 33: echo "T-2: Create a 1M file using O_DIRECT & O_SYNC"`
- `line 35: echo "T-2: Shutdown the fs suddenly"`
- `line 37: echo "T-2: Cycle mount"`
- `line 39: echo "T-2: File contents after cycle mount"`
- Key operational lines include:
- `line 15: _require_scratch_shutdown`
- `line 21: _scratch_mkfs > $seqres.full 2>&1`
- `line 22: _scratch_mount`
- `line 25: $XFS_IO_PROG -fs -c "pwrite -S 0x5a 0 1M" $SCRATCH_MNT/testfile.t1 > /dev/null 2>&1`
- `line 27: _scratch_shutdown`
- `line 29: _scratch_cycle_mount`
- `line 31: _hexdump $SCRATCH_MNT/testfile.t1`
- `line 34: $XFS_IO_PROG -fsd -c "pwrite -S 0x5a 0 1M" $SCRATCH_MNT/testfile.t2 > /dev/null 2>&1`
- `line 36: _scratch_shutdown`
- `line 38: _scratch_cycle_mount`
- `line 40: _hexdump $SCRATCH_MNT/testfile.t2`
- `line 43: $AIO_TEST -a size=1048576 -S -N $SCRATCH_MNT/testfile.t3 > /dev/null 2>&1`
- `line 45: _scratch_shutdown`
- `line 47: _scratch_cycle_mount`
- `line 49: _hexdump $SCRATCH_MNT/testfile.t3`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick shutdown aio`, common helper libraries (`./common/preamble`), and the golden-output file `sources/test-tools/xfstests/tests/generic/737.out` (22 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch`, `_require_scratch_shutdown`, `_require_aiodio aio-dio-write-verify`.

## Risks and Edge Cases

- Direct/AIO coverage depends on alignment, device logical block size, page size, and filesystem direct-I/O semantics.
- Failure-injection paths can leave mounts or synthetic device tables behind if cleanup is interrupted.

## Test Signals

The paired `.out` file has 22 line(s); its first visible signals are: 'QA output created by 737; T-1: Create a 1M file using buff-io & O_SYNC; T-1: Shutdown the fs suddenly; T-1: Cycle mount; T-1: File contents after cycle mount'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, post-remount or failure-injection persistence checks. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
