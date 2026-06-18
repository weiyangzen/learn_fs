# sources/test-tools/xfstests/tests/generic/245

## Purpose

Check that directory renames onto non-empty targets fail Based on a bug report and testcase from Vlado Plaga <rechner@vlado-do.de> According to the rename(2) manpage you can get either EEXIST or ENOTEMPTY as an error for trying to rename a non-empty directory, so just catch the error for ENOTMEMPTY and replace it with the EEXIST output so that either result passes Also, mv v9.4+ modified error message when a nonempty destination directory fails to be overwriteen. It is registered with `_begin_fstest auto quick dir` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `245` plus `_begin_fstest auto quick dir`. Imported libraries: `. ./common/preamble`, `. ./common/filter`. Capability gates: `_require_test`. Local functions: `_cleanup`, `_filter_directory_not_empty`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 19: `dir=$TEST_DIR/test-mv`
- Line 49: `status=0`

## Control Flow

Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 17: `_require_test`
- Line 24: `rm -rf $dir`
- Line 32: `_filter_directory_not_empty()`
- Line 39: `mkdir $dir`
- Line 41: `mkdir $dir/aa`
- Line 42: `mkdir $dir/ab`
- Line 43: `touch $dir/aa/1`
- Line 44: `mkdir $dir/ab/aa`
- Line 45: `touch $dir/ab/aa/2`
- Line 47: `mv $dir/ab/aa/ $dir 2>&1 | _filter_test_dir | _filter_directory_not_empty`

## State and Persistence Behavior

Primary state lives under `$TEST_DIR`, making this a test-device workload rather than a scratch-device destructive test. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `dir`, imports `. ./common/preamble`, `. ./common/filter`, and uses capability gates such as `_require_test`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.

## Test Signals

The pass signal is silence from the helper program and final `status=0`. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
