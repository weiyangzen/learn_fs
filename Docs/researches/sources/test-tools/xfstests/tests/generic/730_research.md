# sources/test-tools/xfstests/tests/generic/730

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/730`. Test proper file system shut down when the block device is removed underneath and there is dirty data. It is registered with `_begin_fstest auto quick`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 61 source line(s).
- Harness registration: `_begin_fstest auto quick`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/scsi_debug`.
- Capability and skip gates: `_require_test`, `_require_block_device $TEST_DEV`, `_require_scsi_debug`.
- Local shell functions: `_cleanup`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `size=$(_small_fs_size_mb 256)`
- `SCSI_DEBUG_DEV=`_get_scsi_debug_dev 512 512 0 $size``
- `SCRATCH_DEV=$SCSI_DEBUG_DEV _require_scratch_shutdown`
- `SCSI_DEBUG_MNT="$TEST_DIR/scsi_debug_$seq"`

## Control Flow

- Capability gating runs first through `_require_test`, `_require_block_device $TEST_DEV`, `_require_scsi_debug`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- User-visible phase markers include:
- `line 36: echo "SCSI debug device $SCSI_DEBUG_DEV" >>$seqres.full`
- `line 52: echo 1 > /sys/block/$(_short_dev $SCSI_DEBUG_DEV)/device/delete`
- Key operational lines include:
- `line 15: _unmount $SCSI_DEBUG_MNT >>$seqres.full 2>&1`
- `line 30: _exclude_scratch_mount_option "dax"`
- `line 35: SCRATCH_DEV=$SCSI_DEBUG_DEV _require_scratch_shutdown`
- `line 38: run_check _mkfs_dev $SCSI_DEBUG_DEV`
- `line 43: run_check _mount $SCSI_DEBUG_DEV $SCSI_DEBUG_MNT`
- `line 46: $XFS_IO_PROG -f -c "pwrite 0 1M" $SCSI_DEBUG_MNT/testfile >>$seqres.full`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Synthetic block-device state can be introduced through device-mapper, loop, SCSI debug, or huge-device helpers and must be cleaned even on failure. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/scsi_debug`), and the golden-output file `sources/test-tools/xfstests/tests/generic/730.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_test`, `_require_block_device $TEST_DEV`, `_require_scsi_debug`.

## Risks and Edge Cases

- Failure-injection paths can leave mounts or synthetic device tables behind if cleanup is interrupted.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 730; cat: -: Input/output error'. Runtime pass/fail is also signaled by post-remount or failure-injection persistence checks. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
