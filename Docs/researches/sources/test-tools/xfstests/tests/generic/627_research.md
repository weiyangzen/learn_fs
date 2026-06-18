# sources/test-tools/xfstests/tests/generic/627

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/627`. AIO/DIO stress test Run random AIO/DIO activity on an file system with unwritten regions This test verifies that the an unwritten extent is properly marked as written after writing into it. There was a hard-to-hit bug which would occasionally trigger with ext4 for which this test was a reproducer. This has been fixed after moving ext4 to use iomap for Direct I/O's, although as of this writing, there are still some occasional failures on ext4 when block size < page size. It is registered with `_begin_fstest auto aio rw stress prealloc`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 90 source line(s).
- Harness registration: `_begin_fstest auto aio rw stress prealloc`.
- Imported common libraries: `./common/preamble`, `./common/filter`.
- Capability and skip gates: `_require_test`, `_require_scratch`, `_require_odirect`, `_require_aio`, `_require_block_device $SCRATCH_DEV`, `_require_fio $fio_config`, `_require_xfs_io_command "falloc"`.
- Local shell functions: none visible.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `fio_config=$tmp.fio`
- `fio_out=$tmp.fio.out`
- `NUM_JOBS=$((4*LOAD_FACTOR))`
- `BLK_DEV_SIZE=`blockdev --getsz $SCRATCH_DEV``
- `FILE_SIZE=$(((BLK_DEV_SIZE * 512) * 3 / 4))`
- `max_file_size=$((5 * 1024 * 1024 * 1024))`
- `FILE_SIZE=$max_file_size`
- `SIZE=$((FILE_SIZE / 2))`
- `ioengine=libaio`
- `bs=128k`
- `directory=${SCRATCH_MNT}`
- `filesize=${FILE_SIZE}`

## Control Flow

- Capability gating runs first through `_require_test`, `_require_scratch`, `_require_odirect`, `_require_aio`, `_require_block_device $SCRATCH_DEV`, plus 2 more.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- User-visible phase markers include:
- `line 82: echo ""`
- `line 83: echo "Run fio with random aio-dio pattern"`
- `line 84: echo ""`
- Key operational lines include:
- `line 22: fio_config=$tmp.fio`
- `line 23: fio_out=$tmp.fio.out`
- `line 44: cat >$fio_config <<EOF`
- `line 57: fallocate=native`
- `line 76: _require_fio $fio_config`
- `line 77: _require_xfs_io_command "falloc"`
- `line 79: _scratch_mkfs >> $seqres.full 2>&1`
- `line 80: _scratch_mount`
- `line 83: echo "Run fio with random aio-dio pattern"`
- `line 85: cat $fio_config >> $seqres.full`
- `line 86: $FIO_PROG $fio_config --output=$fio_out`
- `line 87: cat $fio_out >> $seqres.full`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto aio rw stress prealloc`, common helper libraries (`./common/preamble`, `./common/filter`), and the golden-output file `sources/test-tools/xfstests/tests/generic/627.out` (4 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_test`, `_require_scratch`, `_require_odirect`, `_require_aio`, `_require_block_device $SCRATCH_DEV`, `_require_fio $fio_config`, `_require_xfs_io_command "falloc"`.

## Risks and Edge Cases

- Direct/AIO coverage depends on alignment, device logical block size, page size, and filesystem direct-I/O semantics.

## Test Signals

The paired `.out` file has 4 line(s); its first visible signals are: 'QA output created by 627; Run fio with random aio-dio pattern'. Runtime pass/fail is primarily the command exit status plus golden-output comparison. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
