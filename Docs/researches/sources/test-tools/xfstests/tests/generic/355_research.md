# sources/test-tools/xfstests/tests/generic/355

## Purpose

Test clear of suid/sgid on direct write create testfile and set base ownership & permission. It is registered with `_begin_fstest auto quick perms` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `355` plus `_begin_fstest auto quick perms`. Imported libraries: `. ./common/preamble`, `. ./common/filter`. Capability gates: `_require_test`, `_require_user`, `_require_odirect`, `_require_chown`. Local functions: `do_io`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 20: `testfile=$TEST_DIR/$seq.test`
- Line 65: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 29 `echo "Check that suid/sgid bits are cleared after direct write"`, line 32 `echo "this is a test" >> $testfile`, line 36 `echo "== with no exec perm"`, line 38 `echo -n "before: "; stat -c '%A' $testfile`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 15: `_require_test`
- Line 18: `_require_chown`
- Line 21: `rm -f $testfile`
- Line 25: `_su $qa_user -c "$XFS_IO_PROG -d -c 'pwrite 0 4k' $testfile" \`
- Line 33: `chmod 644 $testfile`
- Line 34: `chown $qa_user:$qa_user $testfile`
- Line 37: `chmod ug+s $testfile`
- Line 38: `echo -n "before: "; stat -c '%A' $testfile`
- Line 40: `echo -n "after: "; stat -c '%A' $testfile`
- Line 43: `chmod ug+s $testfile`
- Line 44: `chmod u+x $testfile`
- Line 45: `echo -n "before: "; stat -c '%A' $testfile`
- Line 47: `echo -n "after: "; stat -c '%A' $testfile`
- Line 62: `echo -n "after: "; stat -c '%A' $testfile`

## State and Persistence Behavior

Primary state lives under `$TEST_DIR`, making this a test-device workload rather than a scratch-device destructive test. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `perms`, imports `. ./common/preamble`, `. ./common/filter`, and uses capability gates such as `_require_test`, `_require_user`, `_require_odirect`, `_require_chown`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.

## Test Signals

The pass signal is stat/lstat metadata output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
