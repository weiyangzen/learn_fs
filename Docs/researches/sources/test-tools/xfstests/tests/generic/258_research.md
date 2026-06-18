# sources/test-tools/xfstests/tests/generic/258

## Purpose

Test timestamps prior to epoch On 64-bit, ext2/3/4 was sign-extending when read from disk See also commit 4d7bf11d649c72621ca31b8ea12b9c94af380e63 Create a file with a timestamp prior to the epoch Should yield -315593940 (prior to epoch) unmount, remount, and check the timestamp. It is registered with `_begin_fstest auto quick bigtime` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `258` plus `_begin_fstest auto quick bigtime`. Imported libraries: `. ./common/preamble`. Capability gates: `_require_test`, `_require_negative_timestamps`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 19: `TESTFILE=$TEST_DIR/timestamp-test.txt`
- Line 26: `ts=`stat -c %X $TESTFILE``
- Line 38: `ts=`stat -c %X $TESTFILE``
- Line 44: `status=0 ; exit`

## Control Flow

The visible phases are driven by echo markers such as line 22 `echo "Creating file with timestamp of Jan 1, 1960"`, line 25 `echo "Testing for negative seconds since epoch"`, line 28 `echo "Timestamp wrapped: $ts"`, line 33 `echo "Remounting to flush cache"`. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 16: `_require_test`
- Line 23: `touch -t 196001010101 $TESTFILE`
- Line 26: `ts=`stat -c %X $TESTFILE``
- Line 33: `echo "Remounting to flush cache"`
- Line 34: `_test_cycle_mount`
- Line 38: `ts=`stat -c %X $TESTFILE``

## State and Persistence Behavior

Primary state lives under `$TEST_DIR`, making this a test-device workload rather than a scratch-device destructive test. Cycle-mount calls force metadata and extent state through unmount/remount persistence before validation. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `bigtime`, imports `. ./common/preamble`, and uses capability gates such as `_require_test`, `_require_negative_timestamps`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- The main risk is environment drift: missing helper binaries, unsupported filesystem operations, or output formatting changes can make the test skip or fail without indicating a filesystem regression.

## Test Signals

The pass signal is stat/lstat metadata output, explicit `_fail` assertions. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
