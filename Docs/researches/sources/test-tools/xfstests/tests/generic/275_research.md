# sources/test-tools/xfstests/tests/generic/275

## Purpose

The posix write test. When write size is larger than disk free size, should write as much as possible until ENOSPC creator This test requires specific data space usage, skip if we have compression enabled. It is registered with `_begin_fstest auto rw enospc` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `275` plus `_begin_fstest auto rw enospc`. Imported libraries: `. ./common/preamble`, `. ./common/filter`. Capability gates: `_require_scratch`, `_require_no_compress`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 44: `later_file=$SCRATCH_MNT/later`
- Line 71: `_freespace=`$DF_PROG -k $SCRATCH_MNT | tail -n 1 | awk '{print $5}'``
- Line 81: `_filesize=`_get_filesize $later_file``
- Line 86: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 30 `echo "------------------------------"`, line 31 `echo "write until ENOSPC test"`, line 32 `echo "------------------------------"`, line 63 `echo "Pre rm space:" >> $seqres.full`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 19: `_scratch_unmount`
- Line 24: `_require_scratch`
- Line 34: `_scratch_unmount 2>/dev/null`
- Line 35: `_scratch_mkfs_sized $((2 * 1024 * 1024 * 1024)) >>$seqres.full 2>&1`
- Line 36: `_scratch_mount`
- Line 45: `touch $later_file`
- Line 47: `touch $SCRATCH_MNT/tmp$i`
- Line 52: `dd if=/dev/zero of=$SCRATCH_MNT/tmp1 bs=256K count=1 >>$seqres.full 2>&1`
- Line 56: `dd if=/dev/zero of=$SCRATCH_MNT/tmp2 bs=1M >>$seqres.full 2>&1`
- Line 57: `_scratch_sync`
- Line 58: `dd if=/dev/zero of=$SCRATCH_MNT/tmp3 bs=4K >>$seqres.full 2>&1`
- Line 59: `_scratch_sync`
- Line 61: `dd if=/dev/zero of=$SCRATCH_MNT/tmp4 bs=4K oflag=sync >>$seqres.full 2>&1`
- Line 78: `du $later_file >>$seqres.full`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `rw`, `enospc`, imports `. ./common/preamble`, `. ./common/filter`, and uses capability gates such as `_require_scratch`, `_require_no_compress`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.
- ENOSPC cases are deliberately capacity-sensitive and can expose allocator, reservation, or delayed-allocation leaks only when scratch sizing and reserved blocks match the scenario.

## Test Signals

The pass signal is explicit `_fail` assertions. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
