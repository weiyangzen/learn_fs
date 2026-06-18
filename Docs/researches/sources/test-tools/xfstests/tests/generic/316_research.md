# sources/test-tools/xfstests/tests/generic/316

## Purpose

Test Generic fallocate hole punching w/o unwritten extent Standard punch hole tests Delayed allocation punch hole tests Multi hole punch tests Delayed allocation multi punch hole tests success, all done. It is registered with `_begin_fstest auto quick punch fiemap` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `316` plus `_begin_fstest auto quick punch fiemap`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/punch`. Capability gates: `_require_test`, `_require_xfs_io_command "fpunch"`, `_require_xfs_io_command "fiemap"`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 21: `testfile=$TEST_DIR/$seq.$$`
- Line 36: `status=0`

## Control Flow

The script runs linearly after the harness and requirement checks. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 10: `_begin_fstest auto quick punch fiemap`
- Line 17: `_require_test`
- Line 18: `_require_xfs_io_command "fpunch"`
- Line 19: `_require_xfs_io_command "fiemap"`
- Line 24: `_test_generic_punch -u pwrite fpunch fpunch fiemap _filter_hole_fiemap $testfile`
- Line 27: `_test_generic_punch -u -d pwrite fpunch fpunch fiemap _filter_hole_fiemap $testfile`
- Line 30: `_test_generic_punch -u -k pwrite fpunch fpunch fiemap _filter_hole_fiemap $testfile`
- Line 33: `_test_generic_punch -u -d -k pwrite fpunch fpunch fiemap _filter_hole_fiemap $testfile`

## State and Persistence Behavior

Primary state lives under `$TEST_DIR`, making this a test-device workload rather than a scratch-device destructive test. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `punch`, `fiemap`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/punch`, and uses capability gates such as `_require_test`, `_require_xfs_io_command "fpunch"`, `_require_xfs_io_command "fiemap"`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.
- Extent-map output is formatted and filtered, but the test still depends on stable extent flags, logical block addressing, and filesystem support for the ioctl under test.

## Test Signals

The pass signal is filtered extent-map output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
