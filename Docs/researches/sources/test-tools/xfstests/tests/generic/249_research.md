# sources/test-tools/xfstests/tests/generic/249

## Purpose

simple splice(2) test. It is registered with `_begin_fstest auto quick rw` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `249` plus `_begin_fstest auto quick rw`. Imported libraries: `. ./common/preamble`, `. ./common/filter`. Capability gates: `_require_test`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 27: `SRC=$TEST_DIR/$seq.src`
- Line 28: `DST=$TEST_DIR/$seq.dst`
- Line 36: `status=$?`

## Control Flow

The visible phases are driven by echo markers such as line 25 `echo "Feel the serenity."`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 16: `rm -f $tmp.*`
- Line 17: `rm -f $SRC $DST`
- Line 23: `_require_test`
- Line 30: `$XFS_IO_PROG -f -c "pwrite -S 0xa5a55a5a 0 32768k" -c fsync $SRC >> $seqres.full 2>&1`
- Line 32: `$XFS_IO_PROG -f -c "sendfile -i $SRC 0 32768k" -c fsync $DST >> $seqres.full 2>&1`

## State and Persistence Behavior

Primary state lives under `$TEST_DIR`, making this a test-device workload rather than a scratch-device destructive test. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `rw`, imports `. ./common/preamble`, `. ./common/filter`, and uses capability gates such as `_require_test`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- The main risk is environment drift: missing helper binaries, unsupported filesystem operations, or output formatting changes can make the test skip or fail without indicating a filesystem regression.

## Test Signals

The pass signal is explicit `_fail` assertions. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
