# sources/test-tools/xfstests/tests/generic/623

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/623`. Test a write fault scenario on a shutdown fs. It is registered with `_begin_fstest auto quick shutdown mmap`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 34 source line(s).
- Harness registration: `_begin_fstest auto quick shutdown mmap`.
- Imported common libraries: `./common/preamble`, `./common/filter`.
- Capability and skip gates: `_fixed_by_fs_commit xfs e4826691cc7e "xfs: restore shutdown check in mapped write fault path"`, `_require_scratch_nocheck`, `_require_xfs_io_shutdown`.
- Local shell functions: none visible.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `file=$SCRATCH_MNT/file`

## Control Flow

- Capability gating runs first through `_fixed_by_fs_commit xfs e4826691cc7e "xfs: restore shutdown check in mapped write fault path"`, `_require_scratch_nocheck`, `_require_xfs_io_shutdown`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- Key operational lines include:
- `line 10: _begin_fstest auto quick shutdown mmap`
- `line 17: _require_scratch_nocheck`
- `line 20: _scratch_mkfs &>> $seqres.full`
- `line 21: _scratch_mount`
- `line 27: $XFS_IO_PROG -fc "pwrite 0 4k" -c fsync $file | _filter_xfs_io`
- `line 29: $XFS_IO_PROG -x -c "mmap 0 4k" -c "mwrite 0 4k" -c shutdown -c fsync \`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick shutdown mmap`, common helper libraries (`./common/preamble`, `./common/filter`), and the golden-output file `sources/test-tools/xfstests/tests/generic/623.out` (4 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_fixed_by_fs_commit xfs e4826691cc7e "xfs: restore shutdown check in mapped write fault path"`, `_require_scratch_nocheck`, `_require_xfs_io_shutdown`.

## Risks and Edge Cases

- Failure-injection paths can leave mounts or synthetic device tables behind if cleanup is interrupted.
- mmap/page-fault regressions are often race-prone and may manifest as hangs rather than clean command failures.

## Test Signals

The paired `.out` file has 4 line(s); its first visible signals are: 'QA output created by 623; wrote 4096/4096 bytes at offset 0; XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec); fsync: Input/output error'. Runtime pass/fail is also signaled by xfstests output filters, hang/race detection through background work, loops, or timeout windows. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
