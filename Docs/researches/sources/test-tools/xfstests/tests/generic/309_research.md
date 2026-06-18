# sources/test-tools/xfstests/tests/generic/309

## Purpose

Test directory mtime and ctime are updated when moving a file onto an existing file in the directory Regression test for commit: 0b23076 ext3: fix update of mtime and ctime on rename. It is registered with `_begin_fstest auto quick` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `309` plus `_begin_fstest auto quick`. Imported libraries: `. ./common/preamble`, `. ./common/filter`. Capability gates: `_require_test`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 16: `status=0 # success is the default!`
- Line 37: `mtime1=`stat -c %Y $TEST_DIR/testdir_$seq``
- Line 38: `ctime1=`stat -c %Z $TEST_DIR/testdir_$seq``
- Line 43: `mtime2=`stat -c %Y $TEST_DIR/testdir_$seq``
- Line 44: `ctime2=`stat -c %Z $TEST_DIR/testdir_$seq``

## Control Flow

The visible phases are driven by echo markers such as line 31 `echo "Silence is golden"`, line 47 `echo "mtime not updated"`, line 51 `echo "ctime not updated"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 22: `rm -rf $TEST_DIR/testdir_$seq`
- Line 23: `rm -f $TEST_DIR/testfile.$seq`
- Line 29: `_require_test`
- Line 33: `mkdir -p $TEST_DIR/testdir_$seq`
- Line 34: `touch $TEST_DIR/testdir_$seq/testfile`
- Line 35: `touch $TEST_DIR/testfile.$seq`
- Line 37: `mtime1=`stat -c %Y $TEST_DIR/testdir_$seq``
- Line 38: `ctime1=`stat -c %Z $TEST_DIR/testdir_$seq``
- Line 41: `mv $TEST_DIR/testfile.$seq $TEST_DIR/testdir_$seq/testfile`
- Line 43: `mtime2=`stat -c %Y $TEST_DIR/testdir_$seq``
- Line 44: `ctime2=`stat -c %Z $TEST_DIR/testdir_$seq``

## State and Persistence Behavior

Primary state lives under `$TEST_DIR`, making this a test-device workload rather than a scratch-device destructive test. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, imports `. ./common/preamble`, `. ./common/filter`, and uses capability gates such as `_require_test`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.

## Test Signals

The pass signal is stat/lstat metadata output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
