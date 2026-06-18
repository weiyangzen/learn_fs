# sources/test-tools/xfstests/tests/generic/246

## Purpose

Check that truncation after failed writes does not zero too much data Based on a bug report and testcase from Marius Tolzmann <tolzmann@molgen.mpg.de>. It is registered with `_begin_fstest auto quick rw mmap` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `246` plus `_begin_fstest auto quick rw mmap`. Imported libraries: `. ./common/preamble`, `. ./common/filter`. Capability gates: `_require_test`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 20: `file=$TEST_DIR/mmap-writev`
- Line 33: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 29 `echo -n "cccccccccc" > $file`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 13: `_begin_fstest auto quick rw mmap`
- Line 18: `_require_test`
- Line 20: `file=$TEST_DIR/mmap-writev`
- Line 25: `rm -rf $file`
- Line 26: `rm -rf $file.NEW`
- Line 30: `$here/src/t_mmap_writev $file $file.NEW`

## State and Persistence Behavior

Primary state lives under `$TEST_DIR`, making this a test-device workload rather than a scratch-device destructive test. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `rw`, `mmap`, imports `. ./common/preamble`, `. ./common/filter`, and uses capability gates such as `_require_test`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- mmap tests rely on page-cache writeback, timestamp granularity, and correct handling of dirty mappings across fsync, sync, or remount boundaries.

## Test Signals

The pass signal is silence from the helper program and final `status=0`. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
