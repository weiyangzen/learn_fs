# sources/test-tools/xfstests/tests/generic/236

## Purpose

Check ctime updated or not if file linked See also http://marc.info/?l=linux-btrfs&m=127434439020230&w=2 create a file and get its ctime create a link to a file and get existing file's ctime check ctime updated. It is registered with `_begin_fstest auto quick metadata` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `236` plus `_begin_fstest auto quick metadata`. Imported libraries: `. ./common/preamble`. Capability gates: `_require_hardlinks`, `_require_test`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 28: `ctime=`stat -c %Z $TEST_DIR/ouch``
- Line 33: `ctime2=`stat -c %Z $TEST_DIR/ouch``
- Line 45: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 37 `echo "ctime: $ctime -> $ctime2 "`, line 38 `echo "Fatal error: ctime not updated after link"`, line 43 `echo "Test over."`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 16: `rm -f $TEST_DIR/ouch*`
- Line 22: `_require_test`
- Line 24: `rm -f $TEST_DIR/ouch*`
- Line 27: `touch $TEST_DIR/ouch`
- Line 28: `ctime=`stat -c %Z $TEST_DIR/ouch``
- Line 33: `ctime2=`stat -c %Z $TEST_DIR/ouch``

## State and Persistence Behavior

Primary state lives under `$TEST_DIR`, making this a test-device workload rather than a scratch-device destructive test. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `metadata`, imports `. ./common/preamble`, and uses capability gates such as `_require_hardlinks`, `_require_test`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- The main risk is environment drift: missing helper binaries, unsupported filesystem operations, or output formatting changes can make the test skip or fail without indicating a filesystem regression.

## Test Signals

The pass signal is stat/lstat metadata output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
