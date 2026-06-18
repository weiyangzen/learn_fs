# sources/test-tools/xfstests/tests/generic/365

## Purpose

Regression test for sub-fsblock key handling errors in GETFSMAP This makes sure there is free space surrounded by allocated blocks, which is needed for some sub tests. It is registered with `_begin_fstest auto rmap fsmap` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `365` plus `_begin_fstest auto rmap fsmap`. Imported libraries: `. ./common/preamble`, `. ./common/filter`. Capability gates: `_require_xfs_io_command "fsmap"`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "fpunch"`, `_require_scratch`. Local functions: `find_freesp`, `filter_fsmap`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 29: `blksz=$(_get_block_size "$SCRATCH_MNT")`
- Line 56: `freesp="$(find_freesp)"`
- Line 58: `freesp_start="$(echo "$freesp" | cut -d ':' -f 1)"`
- Line 59: `freesp_end="$(echo "$freesp" | cut -d ':' -f 2)"`
- Line 86: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 60 `echo "$freesp:$freesp_start:$freesp_end" >> $seqres.full`, line 62 `echo "test incorrect setting of high key"`, line 65 `echo "test missing free space extent"`, line 69 `echo "test whatever came before freesp"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 10: `_begin_fstest auto rmap fsmap`
- Line 13: `"xfs: Fix the owner setting issue for rmap query in xfs fsmap"`
- Line 15: `"xfs: Fix missing interval for missing_owner in xfs fsmap"`
- Line 21: `_require_xfs_io_command "fsmap"`
- Line 22: `_require_xfs_io_command "falloc"`
- Line 23: `_require_xfs_io_command "fpunch"`
- Line 24: `_require_scratch`
- Line 26: `_scratch_mkfs >> $seqres.full`
- Line 27: `_scratch_mount`
- Line 36: `$XFS_IO_PROG -fc 'falloc 0 3M' -c 'fpunch 1M 1M' -c 'fsync' $SCRATCH_MNT/f`
- Line 38: `$XFS_IO_PROG -c 'fsmap' $SCRATCH_MNT >> $seqres.full`
- Line 41: `$XFS_IO_PROG -c 'fsmap -d' $SCRATCH_MNT | tr '.[]:' ' ' | \`
- Line 46: `filter_fsmap() {`
- Line 83: `filter_fsmap`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `rmap`, `fsmap`, imports `. ./common/preamble`, `. ./common/filter`, and uses capability gates such as `_require_xfs_io_command "fsmap"`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "fpunch"`, `_require_scratch`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.
- Extent-map output is formatted and filtered, but the test still depends on stable extent flags, logical block addressing, and filesystem support for the ioctl under test.
- Several checks can intentionally call `_notrun`; this is expected for unsupported geometry or feature combinations and should be distinguished from a failing assertion.

## Test Signals

The pass signal is filtered extent-map output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
