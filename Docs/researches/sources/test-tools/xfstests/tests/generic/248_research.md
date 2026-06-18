# sources/test-tools/xfstests/tests/generic/248

## Purpose

Test for pwrite hang problem when writing from mmaped buffer of the same page Modify as appropriate success, all done. It is registered with `_begin_fstest auto quick rw mmap` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `248` plus `_begin_fstest auto quick rw mmap`. Imported libraries: `. ./common/preamble`, `. ./common/filter`. Capability gates: `_require_test`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 26: `TESTFILE=$TEST_DIR/test_file`
- Line 27: `TEST_PROG=$here/src/pwrite_mmap_blocked`
- Line 32: `status=0`

## Control Flow

Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 10: `_begin_fstest auto quick rw mmap`
- Line 16: `rm -f $tmp.* $TESTFILE`
- Line 24: `_require_test`
- Line 27: `TEST_PROG=$here/src/pwrite_mmap_blocked`

## State and Persistence Behavior

Primary state lives under `$TEST_DIR`, making this a test-device workload rather than a scratch-device destructive test. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `rw`, `mmap`, imports `. ./common/preamble`, `. ./common/filter`, and uses capability gates such as `_require_test`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- mmap tests rely on page-cache writeback, timestamp granularity, and correct handling of dirty mappings across fsync, sync, or remount boundaries.

## Test Signals

The pass signal is silence from the helper program and final `status=0`. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
