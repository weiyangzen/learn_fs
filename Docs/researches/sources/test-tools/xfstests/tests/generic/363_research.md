# sources/test-tools/xfstests/tests/generic/363

## Purpose

Run fsx with EOF pollution enabled. This provides test coverage for partial EOF page/block zeroing for operations that change file size on failure, replace -q with -d to see post-eof writes in the dump output. It is registered with `_begin_fstest rw auto` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `363` plus `_begin_fstest rw auto`. Imported libraries: `. ./common/preamble`. Capability gates: `_require_test`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 24: `status=0`

## Control Flow

The script runs linearly after the harness and requirement checks. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 14: `_require_test`
- Line 22: `run_fsx "-q -S 0 -e 1 -N 100000"`

## State and Persistence Behavior

The script has little persistent state beyond the files it creates and the xfstests result logs. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `rw`, `auto`, imports `. ./common/preamble`, and uses capability gates such as `_require_test`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.
- Stress tests are randomized or high-iteration workloads, so seeds, scaling helpers, timeouts, and captured stderr are important for reproducibility.

## Test Signals

The pass signal is stress-tool exit status and captured logs. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
