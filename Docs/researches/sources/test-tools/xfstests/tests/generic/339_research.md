# sources/test-tools/xfstests/tests/generic/339

## Purpose

Test that directory hash entries are place in the correct order commit f5ea110 ("xfs: add CRCs to dir2/da node blocks") left the directory with incorrect hash ordering check the scratch device remove all test dirs and let test harness check scratch fs again. It is registered with `_begin_fstest auto dir` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `339` plus `_begin_fstest auto dir`. Imported libraries: `. ./common/preamble`, `. ./common/filter`. Capability gates: `_require_scratch`, `_require_test_program "dirhash_collide"`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 25: `testdir=$SCRATCH_MNT/$seq.$$`
- Line 38: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 23 `echo "Silence is golden"`. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 17: `_require_scratch`
- Line 18: `_require_test_program "dirhash_collide"`
- Line 20: `_scratch_mkfs >>$seqres.full 2>&1`
- Line 21: `_scratch_mount`
- Line 26: `mkdir -p $testdir`
- Line 30: `_scratch_unmount`
- Line 31: `_check_scratch_fs`
- Line 34: `_scratch_mount`
- Line 35: `rm -rf $testdir`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `dir`, imports `. ./common/preamble`, `. ./common/filter`, and uses capability gates such as `_require_scratch`, `_require_test_program "dirhash_collide"`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.

## Test Signals

The pass signal is silence from the helper program and final `status=0`. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
