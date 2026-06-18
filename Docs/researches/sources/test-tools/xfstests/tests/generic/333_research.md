# sources/test-tools/xfstests/tests/generic/333

## Purpose

Test for races or FS corruption when trying to hit ENOSPC while DIO writing to a file that's also the source of a reflink operation. It is registered with `_begin_fstest auto clone` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `333` plus `_begin_fstest auto clone`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`. Capability gates: `_require_scratch_reflink`, `_require_cp_reflink`, `_require_odirect`. Local functions: `_cleanup`, `snappy`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 35: `testdir=$SCRATCH_MNT/test-$seq`
- Line 36: `finished_file=$tmp.finished`
- Line 38: `abort_file=$tmp.abort`
- Line 42: `loops=1024`
- Line 43: `nr_loops=$((loops - 1))`
- Line 44: `blksz=65536`
- Line 53: `n=0`
- Line 55: `out="$(_cp_reflink $testdir/file1 $testdir/snap_$n 2>&1)"`

## Control Flow

The visible phases are driven by echo markers such as line 31 `echo "Format and mount"`, line 46 `echo "Initialize file"`, line 47 `echo >> $seqres.full`, line 57 `echo $out | grep -q "No space left" && break`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 19: `rm -rf $tmp.*`
- Line 27: `_require_scratch_reflink`
- Line 28: `_require_cp_reflink`
- Line 31: `echo "Format and mount"`
- Line 32: `_scratch_mkfs_sized $((400 * 1048576)) > $seqres.full 2>&1`
- Line 33: `_scratch_mount >> $seqres.full 2>&1`
- Line 37: `rm -rf $finished_file`
- Line 39: `rm -rf $abort_file`
- Line 40: `mkdir $testdir`
- Line 48: `_pwrite_byte 0x61 0 $((loops * blksz)) $testdir/file1 >> $seqres.full`
- Line 49: `_scratch_cycle_mount`
- Line 55: `out="$(_cp_reflink $testdir/file1 $testdir/snap_$n 2>&1)"`
- Line 62: `touch $abort_file`
- Line 77: `touch $finished_file`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Cycle-mount calls force metadata and extent state through unmount/remount persistence before validation. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `clone`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, and uses capability gates such as `_require_scratch_reflink`, `_require_cp_reflink`, `_require_odirect`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Reflink coverage is sensitive to extent alignment, delayed allocation, unwritten extents, and page-size dependent block geometry, so comparisons against check files are the main correctness guard.
- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.
- ENOSPC cases are deliberately capacity-sensitive and can expose allocator, reservation, or delayed-allocation leaks only when scratch sizing and reserved blocks match the scenario.

## Test Signals

The pass signal is silence from the helper program and final `status=0`. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
