# sources/test-tools/xfstests/tests/generic/226

## Purpose

Test for prealloc space leaks by rewriting the same file in a loop Buffer size argument supplied to xfs_io "pwrite" command. It is registered with `_begin_fstest auto enospc` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `226` plus `_begin_fstest auto enospc`. Imported libraries: `. ./common/preamble`. Capability gates: `_require_scratch`, `_require_odirect`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 23: `loops=16`
- Line 26: `buffer="-b $(expr 512 \* 1024)"`
- Line 50: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 19 `echo "--> mkfs 256m filesystem"`, line 28 `echo "--> $loops buffered 64m writes in a loop"`, line 30 `echo -n "$I "`, line 36 `echo`. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 14: `_require_scratch`
- Line 18: `_scratch_unmount 2>/dev/null`
- Line 20: `_scratch_mkfs_sized `expr 256 \* 1024 \* 1024` >> $seqres.full 2>&1`
- Line 21: `_scratch_mount`
- Line 31: `$XFS_IO_PROG -f \`
- Line 33: `rm -f $SCRATCH_MNT/test`
- Line 37: `_scratch_cycle_mount`
- Line 42: `$XFS_IO_PROG -f -d \`
- Line 44: `rm -f $SCRATCH_MNT/test`
- Line 48: `_scratch_unmount`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Cycle-mount calls force metadata and extent state through unmount/remount persistence before validation. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `enospc`, imports `. ./common/preamble`, and uses capability gates such as `_require_scratch`, `_require_odirect`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.
- ENOSPC cases are deliberately capacity-sensitive and can expose allocator, reservation, or delayed-allocation leaks only when scratch sizing and reserved blocks match the scenario.

## Test Signals

The pass signal is silence from the helper program and final `status=0`. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
