# sources/test-tools/xfstests/tests/generic/677

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/677`. Test that after a full fsync of a file with preallocated extents beyond the file's size, if a power failure happens, the preallocated extents still exist after we mount the filesystem. It is registered with `_begin_fstest auto quick log prealloc fiemap`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 87 source line(s).
- Harness registration: `_begin_fstest auto quick log prealloc fiemap`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/dmflakey`, `./common/punch`.
- Capability and skip gates: `_require_scratch`, `_require_dm_target flakey`, `_require_xfs_io_command "falloc" "-k"`, `_require_xfs_io_command "fiemap"`, `_require_odirect`, `_require_metadata_journaling $SCRATCH_DEV`, `_require_congruent_file_oplen $SCRATCH_MNT 1048576`.
- Local shell functions: `_cleanup`.
- External `$here/src` helpers: none visible.

## Control Flow

- Capability gating runs first through `_require_scratch`, `_require_dm_target flakey`, `_require_xfs_io_command "falloc" "-k"`, `_require_xfs_io_command "fiemap"`, `_require_odirect`, plus 2 more.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- User-visible phase markers include:
- `line 80: echo "List of extents after power failure:"`
- Key operational lines include:
- `line 16: _cleanup_flakey`
- `line 28: _require_xfs_io_command "falloc" "-k"`
- `line 34: _scratch_mkfs >>$seqres.full 2>&1`
- `line 36: _init_flakey`
- `line 37: _scratch_mount`
- `line 53: $XFS_IO_PROG -f -d -c "pwrite -b 4K 0 16M" $SCRATCH_MNT/foo | _filter_xfs_io`
- `line 58: $XFS_IO_PROG -c "falloc -k 16M 1M" $SCRATCH_MNT/foo`
- `line 59: $XFS_IO_PROG -c "falloc -k 20M 1M" $SCRATCH_MNT/foo`
- `line 65: _scratch_sync`
- `line 72: $XFS_IO_PROG -c "pwrite 0 4K" -c "fsync" $SCRATCH_MNT/foo | _filter_xfs_io`
- `line 76: _flakey_drop_and_remount`
- `line 81: $XFS_IO_PROG -c "fiemap -v" $SCRATCH_MNT/foo | _filter_fiemap`
- `line 83: _scratch_unmount`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Synthetic block-device state can be introduced through device-mapper, loop, SCSI debug, or huge-device helpers and must be cleaned even on failure. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick log prealloc fiemap`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/dmflakey`, `./common/punch`), and the golden-output file `sources/test-tools/xfstests/tests/generic/677.out` (10 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch`, `_require_dm_target flakey`, `_require_xfs_io_command "falloc" "-k"`, `_require_xfs_io_command "fiemap"`, `_require_odirect`, `_require_metadata_journaling $SCRATCH_DEV`, `_require_congruent_file_oplen $SCRATCH_MNT 1048576`.

## Risks and Edge Cases

- Direct/AIO coverage depends on alignment, device logical block size, page size, and filesystem direct-I/O semantics.
- Failure-injection paths can leave mounts or synthetic device tables behind if cleanup is interrupted.

## Test Signals

The paired `.out` file has 10 line(s); its first visible signals are: 'QA output created by 677; wrote 16777216/16777216 bytes at offset 0; XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec); wrote 4096/4096 bytes at offset 0; XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec)'. Runtime pass/fail is also signaled by xfstests output filters, post-remount or failure-injection persistence checks. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
