# sources/test-tools/xfstests/tests/generic/362

## Purpose

Test that doing a direct IO append write to a file when the input buffer was not yet faulted in, does not result in an incorrect file size NFS forbade open with O_APPEND|O_DIRECT On error the test program writes messages to stderr, causing a golden output mismatch and making the test fail success, all done. It is registered with `_begin_fstest auto quick` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `362` plus `_begin_fstest auto quick`. Imported libraries: `. ./common/preamble`. Capability gates: `_require_test`, `_require_odirect`, `_require_test_program dio-append-buf-fault`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 29: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 28 `echo "Silence is golden"`. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 16: `_require_test`
- Line 18: `_require_test_program dio-append-buf-fault`

## State and Persistence Behavior

Primary state lives under `$TEST_DIR`, making this a test-device workload rather than a scratch-device destructive test. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, imports `. ./common/preamble`, and uses capability gates such as `_require_test`, `_require_odirect`, `_require_test_program dio-append-buf-fault`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.

## Test Signals

The pass signal is silence from the helper program and final `status=0`. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
