# sources/test-tools/xfstests/tests/generic/312

## Purpose

ENOSPC in fallocate(2) could corrupt ext4 when file size > 4G Regression test for commit 29ae07b ext4: Fix overflow caused by missing cast in ext4_fallocate() 5G in byte fallocate(2) a 6G(> 4G) file on a 5G fs. It is registered with `_begin_fstest auto quick prealloc enospc` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `312` plus `_begin_fstest auto quick prealloc enospc`. Imported libraries: `. ./common/preamble`, `. ./common/filter`. Capability gates: `_require_xfs_io_command "falloc"`, `_require_scratch`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 22: `fssize=$((2**30 * 5))`
- Line 33: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 27 `echo "Silence is golden"`. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 18: `_require_xfs_io_command "falloc"`
- Line 19: `_require_scratch`
- Line 24: `_scratch_mkfs_sized $fssize >>$seqres.full 2>&1`
- Line 25: `_scratch_mount >>$seqres.full 2>&1`
- Line 30: `$XFS_IO_PROG -f -c "falloc 0 6g" $SCRATCH_MNT/testfile.$seq >>$seqres.full 2>&1`
- Line 32: `_scratch_unmount`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `prealloc`, `enospc`, imports `. ./common/preamble`, `. ./common/filter`, and uses capability gates such as `_require_xfs_io_command "falloc"`, `_require_scratch`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- ENOSPC cases are deliberately capacity-sensitive and can expose allocator, reservation, or delayed-allocation leaks only when scratch sizing and reserved blocks match the scenario.

## Test Signals

The pass signal is silence from the helper program and final `status=0`. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
