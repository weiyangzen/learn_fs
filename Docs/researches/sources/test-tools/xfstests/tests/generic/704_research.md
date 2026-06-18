# sources/test-tools/xfstests/tests/generic/704

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/704`. Make sure logical-sector sized O_DIRECT write is allowed It is registered with `_begin_fstest auto quick`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 53 source line(s).
- Harness registration: `_begin_fstest auto quick`.
- Imported common libraries: `./common/preamble`, `./common/scsi_debug`.
- Capability and skip gates: `_fixed_by_fs_commit xfs 7c71ee78031c "xfs: allow logical-sector sized O_DIRECT"`, `_require_scsi_debug`, `_require_test`, `_require_block_device $TEST_DEV`.
- Local shell functions: `_cleanup`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `size=$(_small_fs_size_mb 256)`
- `SCSI_DEBUG_DEV=`_get_scsi_debug_dev 4096 512 0 $size``
- `SCSI_DEBUG_MNT="$TEST_DIR/scsi_debug_$seq"`

## Control Flow

- Capability gating runs first through `_fixed_by_fs_commit xfs 7c71ee78031c "xfs: allow logical-sector sized O_DIRECT"`, `_require_scsi_debug`, `_require_test`, `_require_block_device $TEST_DEV`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- User-visible phase markers include:
- `line 34: echo "Get a device with 4096 physical sector size and 512 logical sector size"`
- `line 38: echo "mkfs and mount"`
- `line 45: echo "DIO read/write 512 bytes"`
- Key operational lines include:
- `line 17: [ -d "$SCSI_DEBUG_MNT" ] && _unmount $SCSI_DEBUG_MNT 2>/dev/null`
- `line 39: _mkfs_dev $SCSI_DEBUG_DEV || _fail "Can't make $FSTYP on scsi_debug device"`
- `line 43: run_check _mount $SCSI_DEBUG_DEV $SCSI_DEBUG_MNT`
- `line 48: $XFS_IO_PROG -d -f -c "pwrite 0 512" $SCSI_DEBUG_MNT/testfile >> $seqres.full`
- `line 49: $XFS_IO_PROG -d -c "pread 0 512" $SCSI_DEBUG_MNT/testfile >> $seqres.full`

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Synthetic block-device state can be introduced through device-mapper, loop, SCSI debug, or huge-device helpers and must be cleaned even on failure. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick`, common helper libraries (`./common/preamble`, `./common/scsi_debug`), and the golden-output file `sources/test-tools/xfstests/tests/generic/704.out` (6 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_fixed_by_fs_commit xfs 7c71ee78031c "xfs: allow logical-sector sized O_DIRECT"`, `_require_scsi_debug`, `_require_test`, `_require_block_device $TEST_DEV`.

## Risks and Edge Cases

- Direct/AIO coverage depends on alignment, device logical block size, page size, and filesystem direct-I/O semantics.
- Failure-injection paths can leave mounts or synthetic device tables behind if cleanup is interrupted.

## Test Signals

The paired `.out` file has 6 line(s); its first visible signals are: 'QA output created by 704; Get a device with 4096 physical sector size and 512 logical sector size; 4096; 512; mkfs and mount'. Runtime pass/fail is also signaled by hang/race detection through background work, loops, or timeout windows. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
