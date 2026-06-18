# sources/test-tools/xfstests/tests/generic/300

## Purpose

AIO/DIO stress test Run random AIO/DIO activity and fallocate/punch_hole simultaneously Test will operate on huge sparsed file so ENOSPC is expected xfs_io is not required for this test, but it's the best way to verify the test system supports fallocate() for allocation and hole punching. It is registered with `_begin_fstest auto aio enospc preallocrw stress punch` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `300` plus `_begin_fstest auto aio enospc preallocrw stress punch`. Imported libraries: `. ./common/preamble`, `. ./common/filter`. Capability gates: `_require_scratch`, `_require_odirect`, `_require_aio`, `_require_block_device $SCRATCH_DEV`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "fpunch"`, `_require_fio $fio_config`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 14: `fio_config=$tmp.fio`
- Line 15: `fio_out=$tmp.fio.out`
- Line 30: `NUM_JOBS=$((4*LOAD_FACTOR))`
- Line 31: `BLK_DEV_SIZE=`blockdev --getsz $SCRATCH_DEV``
- Line 33: `BLK_DEV_SIZE=1048576`
- Line 35: `FS_SIZE=$((BLK_DEV_SIZE * 512))`
- Line 46: `directory=${SCRATCH_MNT}`
- Line 47: `filesize=${FS_SIZE}`

## Control Flow

The visible phases are driven by echo markers such as line 114 `echo ""`, line 115 `echo "Run fio with random aio-dio pattern"`, line 116 `echo ""`. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 14: `fio_config=$tmp.fio`
- Line 15: `fio_out=$tmp.fio.out`
- Line 20: `_require_scratch`
- Line 27: `_require_xfs_io_command "falloc"`
- Line 28: `_require_xfs_io_command "fpunch"`
- Line 37: `cat >$fio_config <<EOF`
- Line 54: `fallocate=none`
- Line 72: `[falloc_raicer]`
- Line 73: `ioengine=falloc`
- Line 82: `ioengine=falloc`
- Line 101: `verify_async=4`
- Line 109: `_require_fio $fio_config`
- Line 111: `_scratch_mkfs_sized $FS_SIZE >> $seqres.full 2>&1`
- Line 119: `cat $fio_out >> $seqres.full`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `aio`, `enospc`, `preallocrw`, `stress`, `punch`, imports `. ./common/preamble`, `. ./common/filter`, and uses capability gates such as `_require_scratch`, `_require_odirect`, `_require_aio`, `_require_block_device $SCRATCH_DEV`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "fpunch"`, `_require_fio $fio_config`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.
- Block-device fallocate tests rely on scsi_debug discard/write-same emulation and logical-sector alignment, not normal mounted filesystem behavior.
- ENOSPC cases are deliberately capacity-sensitive and can expose allocator, reservation, or delayed-allocation leaks only when scratch sizing and reserved blocks match the scenario.
- Stress tests are randomized or high-iteration workloads, so seeds, scaling helpers, timeouts, and captured stderr are important for reproducibility.

## Test Signals

The pass signal is stress-tool exit status and captured logs. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
