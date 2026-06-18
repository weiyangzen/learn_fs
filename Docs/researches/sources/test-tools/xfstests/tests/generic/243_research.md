# sources/test-tools/xfstests/tests/generic/243

## Purpose

Reflink two large files and DIO CoW them in big chunks This test is dependent on the system page size, so we cannot use md5 in the golden output; we can only compare to a check file. It is registered with `_begin_fstest auto clone` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `243` plus `_begin_fstest auto clone`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`. Capability gates: `_require_scratch_reflink`, `_require_cp_reflink`, `_require_odirect`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 34: `testdir=$SCRATCH_MNT/test-$seq`
- Line 37: `blksz=65536`
- Line 38: `nr=6400`
- Line 39: `filesize=$((blksz * nr))`
- Line 40: `bufnr=1280`
- Line 41: `bufsize=$((blksz * bufnr))`
- Line 43: `free_blocks=$(stat -f -c '%a' $testdir)`
- Line 44: `real_blksz=$(_get_block_size $testdir)`

## Control Flow

The visible phases are driven by echo markers such as line 30 `echo "Format and mount"`, line 49 `echo "Create the original files"`, line 55 `echo "Compare files"`, line 60 `echo "CoW and unmount"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 19: `rm -rf $tmp.* $testdir`
- Line 26: `_require_scratch_reflink`
- Line 27: `_require_cp_reflink`
- Line 30: `echo "Format and mount"`
- Line 31: `_scratch_mkfs > $seqres.full 2>&1`
- Line 32: `_scratch_mount >> $seqres.full 2>&1`
- Line 35: `mkdir $testdir`
- Line 43: `free_blocks=$(stat -f -c '%a' $testdir)`
- Line 50: `$XFS_IO_PROG -f -c "pwrite -S 0x61 -b $bufsize 0 $filesize" $testdir/file1 >> $seqres.full`
- Line 51: `_cp_reflink $testdir/file1 $testdir/file2 >> $seqres.full`
- Line 52: `$XFS_IO_PROG -f -c "pwrite -S 0x61 -b $bufsize 0 $filesize" $testdir/file2.chk >> $seqres.full`
- Line 53: `_scratch_cycle_mount`
- Line 56: `md5sum $testdir/file1 | _filter_scratch`
- Line 68: `md5sum $testdir/file2.chk | _filter_scratch`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Cycle-mount calls force metadata and extent state through unmount/remount persistence before validation. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `clone`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, and uses capability gates such as `_require_scratch_reflink`, `_require_cp_reflink`, `_require_odirect`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Reflink coverage is sensitive to extent alignment, delayed allocation, unwritten extents, and page-size dependent block geometry, so comparisons against check files are the main correctness guard.
- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.
- Several checks can intentionally call `_notrun`; this is expected for unsupported geometry or feature combinations and should be distinguished from a failing assertion.

## Test Signals

The pass signal is filtered `md5sum` output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
