# sources/test-tools/xfstests/tests/generic/703

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/703`. Test that direct IO writes with io_uring and O_DSYNC are durable if a power failure happens after they complete. It is registered with `_begin_fstest auto quick log prealloc io_uring`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 101 source line(s).
- Harness registration: `_begin_fstest auto quick log prealloc io_uring`.
- Imported common libraries: `./common/preamble`, `./common/dmflakey`.
- Capability and skip gates: `_fixed_by_fs_commit btrfs 8184620ae212 "btrfs: fix lost file sync on direct IO write with nowait and dsync iocb"`, `_require_scratch_size $((512 * 1024))`, `_require_odirect`, `_require_io_uring`, `_require_dm_target flakey`, `_require_xfs_io_command "falloc"`, `_require_fio $fio_config`, `_require_metadata_journaling $SCRATCH_DEV`, `_require_congruent_file_oplen $SCRATCH_MNT $((64 * 1024))`, `_require_chattr C`.
- Local shell functions: `_cleanup`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `fio_config=$tmp.fio`
- `fio_out=$tmp.fio.out`
- `test_file="${SCRATCH_MNT}/foo"`
- `ioengine=io_uring`
- `direct=1`
- `bs=64K`
- `sync=1`
- `filename=$test_file`
- `rw=randwrite`
- `runtime=10`
- `digest_before=$(_md5_checksum $test_file)`
- `digest_after=$(_md5_checksum $test_file)`

## Control Flow

- Capability gating runs first through `_fixed_by_fs_commit btrfs 8184620ae212 "btrfs: fix lost file sync on direct IO write with nowait and dsync iocb"`, `_require_scratch_size $((512 * 1024))`, `_require_odirect`, `_require_io_uring`, `_require_dm_target flakey`, plus 5 more.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- User-visible phase markers include:
- `line 74: echo -e "Running fio with config:\n" >> $seqres.full`
- `line 79: echo -e "\nOutput from fio:\n" >> $seqres.full`
- `line 91: echo "Error: not all file data got persisted."`
- `line 92: echo "Digest before power failure: $digest_before"`
- `line 93: echo "Digest after power failure: $digest_after"`
- `line 99: echo "Silence is golden"`
- Key operational lines include:
- `line 15: _cleanup_flakey`
- `line 22: fio_config=$tmp.fio`
- `line 23: fio_out=$tmp.fio.out`
- `line 32: _require_scratch_size $((512 * 1024))`
- `line 36: _require_xfs_io_command "falloc"`
- `line 38: cat >$fio_config <<EOF`
- `line 50: _require_fio $fio_config`
- `line 52: _scratch_mkfs >>$seqres.full 2>&1`
- `line 54: _init_flakey`
- `line 55: _scratch_mount`
- `line 69: $XFS_IO_PROG -c "falloc 0 256M" $test_file`
- `line 72: _scratch_sync`
- `line 74: echo -e "Running fio with config:\n" >> $seqres.full`
- `line 75: cat $fio_config >> $seqres.full`
- `line 77: $FIO_PROG $fio_config --output=$fio_out`
- `line 79: echo -e "\nOutput from fio:\n" >> $seqres.full`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Synthetic block-device state can be introduced through device-mapper, loop, SCSI debug, or huge-device helpers and must be cleaned even on failure. Extended attributes are part of the persistent state being created, replayed, or verified. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick log prealloc io_uring`, common helper libraries (`./common/preamble`, `./common/dmflakey`), and the golden-output file `sources/test-tools/xfstests/tests/generic/703.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_fixed_by_fs_commit btrfs 8184620ae212 "btrfs: fix lost file sync on direct IO write with nowait and dsync iocb"`, `_require_scratch_size $((512 * 1024))`, `_require_odirect`, `_require_io_uring`, `_require_dm_target flakey`, `_require_xfs_io_command "falloc"`, `_require_fio $fio_config`, `_require_metadata_journaling $SCRATCH_DEV`, plus 2 more.

## Risks and Edge Cases

- Direct/AIO coverage depends on alignment, device logical block size, page size, and filesystem direct-I/O semantics.
- Failure-injection paths can leave mounts or synthetic device tables behind if cleanup is interrupted.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 703; Silence is golden'. Runtime pass/fail is also signaled by post-remount or failure-injection persistence checks. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
