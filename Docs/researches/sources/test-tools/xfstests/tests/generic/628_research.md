# sources/test-tools/xfstests/tests/generic/628

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/628`. Make sure that reflink forces the log out if we open the file with O_SYNC or set FS_XFLAG_SYNC on the file. We test that it actually forced the log by using dm-error to shut down the fs without flushing the log and then remounting to check file contents. This is a regression test for commit 5ffce3cc22a0 ("xfs: force the log after remapping a synchronous-writes file") It is registered with `_begin_fstest auto quick rw clone eio`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 108 source line(s).
- Harness registration: `_begin_fstest auto quick rw clone eio`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/reflink`, `./common/dmerror`.
- Capability and skip gates: `_require_scratch_reflink`, `_require_dm_target error`, `_require_xfs_io_command "chattr" "s"`, `_require_cp_reflink`, `_require_metadata_journaling $SCRATCH_DEV`.
- Local shell functions: `_cleanup`.
- External `$here/src` helpers: none visible.

## Control Flow

- Capability gating runs first through `_require_scratch_reflink`, `_require_dm_target error`, `_require_xfs_io_command "chattr" "s"`, `_require_cp_reflink`, `_require_metadata_journaling $SCRATCH_DEV`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 43: echo "test o_sync write"`
- `line 61: echo "test reflink flag not set o_sync"`
- `line 71: echo "test reflink flag already set o_sync"`
- `line 88: echo "test reflink flag not set iflag"`
- `line 98: echo "test reflink flag already set iflag"`
- Key operational lines include:
- `line 21: _dmerror_unmount`
- `line 22: _dmerror_cleanup`
- `line 30: _require_scratch_reflink`
- `line 33: _require_cp_reflink`
- `line 36: _scratch_mkfs > $seqres.full`
- `line 38: _dmerror_init`
- `line 39: _dmerror_mount`
- `line 44: $XFS_IO_PROG -x -f -s -c "pwrite -S 0x58 0 1m -b 1m" $SCRATCH_MNT/0 >> $seqres.full`
- `line 45: _dmerror_load_error_table`
- `line 46: _dmerror_unmount`
- `line 47: _dmerror_load_working_table`
- `line 48: _dmerror_mount`
- `line 49: md5sum $SCRATCH_MNT/0 | _filter_scratch`
- `line 52: $XFS_IO_PROG -f -c 'pwrite -S 0x58 0 1m -b 1m' $SCRATCH_MNT/a >> $seqres.full`
- `line 53: $XFS_IO_PROG -f -c 'pwrite -S 0x59 0 1m -b 1m' $SCRATCH_MNT/c >> $seqres.full`
- `line 54: _cp_reflink $SCRATCH_MNT/a $SCRATCH_MNT/e`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Synthetic block-device state can be introduced through device-mapper, loop, SCSI debug, or huge-device helpers and must be cleaned even on failure. Extended attributes are part of the persistent state being created, replayed, or verified. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick rw clone eio`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/reflink`, `./common/dmerror`), and the golden-output file `sources/test-tools/xfstests/tests/generic/628.out` (15 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch_reflink`, `_require_dm_target error`, `_require_xfs_io_command "chattr" "s"`, `_require_cp_reflink`, `_require_metadata_journaling $SCRATCH_DEV`.

## Risks and Edge Cases

- Failure-injection paths can leave mounts or synthetic device tables behind if cleanup is interrupted.
- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 15 line(s); its first visible signals are: 'QA output created by 628; test o_sync write; 310f146ce52077fcd3308dcbe7632bb2  SCRATCH_MNT/0; test reflink flag not set o_sync; 310f146ce52077fcd3308dcbe7632bb2  SCRATCH_MNT/a'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, xfstests output filters, post-remount or failure-injection persistence checks. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
