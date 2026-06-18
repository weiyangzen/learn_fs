# sources/test-tools/xfstests/tests/generic/296

## Purpose

- Create two reflinked files a byte longer than a block - Rewrite the whole file. It is registered with `_begin_fstest auto quick clone` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `296` plus `_begin_fstest auto quick clone`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`. Capability gates: `_require_scratch_reflink`, `_require_cp_reflink`, `_require_fs_space $SCRATCH_MNT $((filesize / 1024 * 3 * 5 / 4))`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 24: `testdir=$SCRATCH_MNT/test-$seq`
- Line 27: `blksz=65536`
- Line 28: `nr=128`
- Line 29: `filesize=$((blksz * nr))`
- Line 30: `bufnr=16`
- Line 31: `bufsize=$((blksz * bufnr))`
- Line 33: `real_blksz=$(_get_block_size "$testdir")`
- Line 58: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 20 `echo "Format and mount"`, line 36 `echo "Create the original files"`, line 42 `echo "Compare files"`, line 47 `echo "CoW and unmount"`. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 17: `_require_scratch_reflink`
- Line 18: `_require_cp_reflink`
- Line 20: `echo "Format and mount"`
- Line 21: `_scratch_mkfs > $seqres.full 2>&1`
- Line 22: `_scratch_mount >> $seqres.full 2>&1`
- Line 25: `mkdir $testdir`
- Line 37: `$XFS_IO_PROG -f -c "pwrite -S 0x61 -b $bufsize 0 $((filesize + 1))" $testdir/file1 >> $seqres.full`
- Line 38: `_cp_reflink $testdir/file1 $testdir/file2 >> $seqres.full`
- Line 39: `$XFS_IO_PROG -f -c "pwrite -S 0x61 -b $bufsize 0 $((filesize + 1))" $testdir/file2.chk >> $seqres.full`
- Line 40: `_scratch_cycle_mount`
- Line 43: `md5sum $testdir/file1 | _filter_scratch`
- Line 44: `md5sum $testdir/file2 | _filter_scratch`
- Line 45: `md5sum $testdir/file2.chk | _filter_scratch`
- Line 55: `md5sum $testdir/file2.chk | _filter_scratch`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Cycle-mount calls force metadata and extent state through unmount/remount persistence before validation. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `clone`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, and uses capability gates such as `_require_scratch_reflink`, `_require_cp_reflink`, `_require_fs_space $SCRATCH_MNT $((filesize / 1024 * 3 * 5 / 4))`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Reflink coverage is sensitive to extent alignment, delayed allocation, unwritten extents, and page-size dependent block geometry, so comparisons against check files are the main correctness guard.

## Test Signals

The pass signal is filtered `md5sum` output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
