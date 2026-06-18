# sources/test-tools/xfstests/tests/generic/299

## Purpose

AIO/DIO stress test Run random AIO/DIO activity and fallocate/truncate simultaneously Test will operate on huge sparsed files so ENOSPC is expected. It is registered with `_begin_fstest auto aio enospc rw stress prealloc` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `299` plus `_begin_fstest auto aio enospc rw stress prealloc`. Imported libraries: `. ./common/preamble`, `. ./common/filter`. Capability gates: `_require_test`, `_require_scratch`, `_require_odirect`, `_require_aio`, `_require_block_device $SCRATCH_DEV`, `_require_xfs_io_command "falloc"`, `_require_fio $fio_config`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 14: `fio_config=$tmp.fio`
- Line 15: `fio_out=$tmp.fio.out`
- Line 27: `NUM_JOBS=$((4*LOAD_FACTOR))`
- Line 28: `BLK_DEV_SIZE=`blockdev --getsz $SCRATCH_DEV``
- Line 29: `FILE_SIZE=$((BLK_DEV_SIZE * 512))`
- Line 31: `max_file_size=$(_get_max_file_size $TEST_DIR)`
- Line 33: `FILE_SIZE=$max_file_size`
- Line 42: `ioengine=libaio`

## Control Flow

The visible phases are driven by echo markers such as line 102 `echo ""`, line 103 `echo "Run fio with random aio-dio pattern"`, line 104 `echo ""`, line 108 `echo "Start fallocate/truncate loop"`. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 14: `fio_config=$tmp.fio`
- Line 15: `fio_out=$tmp.fio.out`
- Line 20: `_require_test`
- Line 21: `_require_scratch`
- Line 25: `_require_xfs_io_command "falloc"`
- Line 36: `cat >$fio_config <<EOF`
- Line 52: `fallocate=none`
- Line 73: `verify_async=4`
- Line 88: `verify_async=4`
- Line 97: `_require_fio $fio_config`
- Line 99: `_scratch_mkfs >> $seqres.full 2>&1`
- Line 100: `_scratch_mount`
- Line 103: `echo "Run fio with random aio-dio pattern"`
- Line 124: `cat $fio_out >> $seqres.full`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. It may also use `$TEST_DIR` for non-destructive helper programs or limit checks. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `aio`, `enospc`, `rw`, `stress`, `prealloc`, imports `. ./common/preamble`, `. ./common/filter`, and uses capability gates such as `_require_test`, `_require_scratch`, `_require_odirect`, `_require_aio`, `_require_block_device $SCRATCH_DEV`, `_require_xfs_io_command "falloc"`, `_require_fio $fio_config`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.
- Block-device fallocate tests rely on scsi_debug discard/write-same emulation and logical-sector alignment, not normal mounted filesystem behavior.
- ENOSPC cases are deliberately capacity-sensitive and can expose allocator, reservation, or delayed-allocation leaks only when scratch sizing and reserved blocks match the scenario.
- Stress tests are randomized or high-iteration workloads, so seeds, scaling helpers, timeouts, and captured stderr are important for reproducibility.

## Test Signals

The pass signal is stress-tool exit status and captured logs. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
