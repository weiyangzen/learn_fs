# sources/test-tools/xfstests/tests/generic/228

## Purpose

Check if fallocate respects RLIMIT_FSIZE generic, but xfs_io's fallocate must work only Linux supports fallocate Sanity check to see if fallocate works Check if we have good enough space available Set the FSIZE ulimit to 100MB and check xfs_io will receive SIGXFSZ signal, if not handled it will trigger a coredump And in bash 5.3.x, bash will always output the command/script triggering the. It is registered with `_begin_fstest rw auto prealloc quick` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `228` plus `_begin_fstest rw auto prealloc quick`. Imported libraries: `. ./common/preamble`. Capability gates: `_require_test`, `_require_xfs_io_command "falloc"`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 22: `avail=`df -P $TEST_DIR | awk 'END {print $4}'``
- Line 27: `flim=`ulimit -f``
- Line 48: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 31 `echo "File size limit is now set to 100 MB."`, line 32 `echo "Let us try to preallocate 101 MB. This should fail."`, line 42 `echo "Let us now try to preallocate 50 MB. This should succeed."`, line 46 `echo "Test over."`. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 14: `_require_test`
- Line 16: `[ -n "$XFS_IO_PROG" ] || _notrun "xfs_io executable not found"`
- Line 19: `_require_xfs_io_command "falloc"`
- Line 22: `avail=`df -P $TEST_DIR | awk 'END {print $4}'``
- Line 26: `ulimit -f 102400`
- Line 27: `flim=`ulimit -f``
- Line 28: `[ "$flim" != "unlimited" ] || _notrun "Unable to set FSIZE ulimit"`
- Line 29: `[ "$flim" -eq 102400 ] || _notrun "FSIZE ulimit is not correct (100 MB)"`
- Line 39: `bash -c "trap '' SIGXFSZ; $XFS_IO_PROG -f -c 'falloc 0 101m' $TEST_DIR/ouch"`
- Line 40: `rm -f $TEST_DIR/ouch`
- Line 43: `$XFS_IO_PROG -f -c 'falloc 0 50m' $TEST_DIR/ouch`
- Line 44: `rm -f $TEST_DIR/ouch`

## State and Persistence Behavior

Primary state lives under `$TEST_DIR`, making this a test-device workload rather than a scratch-device destructive test. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `rw`, `auto`, `prealloc`, `quick`, imports `. ./common/preamble`, and uses capability gates such as `_require_test`, `_require_xfs_io_command "falloc"`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- The main risk is environment drift: missing helper binaries, unsupported filesystem operations, or output formatting changes can make the test skip or fail without indicating a filesystem regression.
- Several checks can intentionally call `_notrun`; this is expected for unsupported geometry or feature combinations and should be distinguished from a failing assertion.

## Test Signals

The pass signal is silence from the helper program and final `status=0`. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
