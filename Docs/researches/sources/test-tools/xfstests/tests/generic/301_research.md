# sources/test-tools/xfstests/tests/generic/301

## Purpose

Test fragmentation after a lot of random CoW: - Create two reflinked files - Buffered write to random offsets to scatter CoW reservations - Check the number of extents. It is registered with `_begin_fstest auto quick clone fiemap` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `301` plus `_begin_fstest auto quick clone fiemap`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`. Capability gates: `_require_scratch_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "fiemap"`, `_require_fs_space $SCRATCH_MNT $((filesize / 1024 * 3 * 5 / 4))`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 27: `testdir=$SCRATCH_MNT/test-$seq`
- Line 30: `blksz=65536`
- Line 31: `nr=128`
- Line 32: `filesize=$((blksz * nr))`
- Line 33: `bufnr=16`
- Line 34: `bufsize=$((blksz * bufnr))`
- Line 37: `real_blksz=$(_get_block_size $testdir)`
- Line 38: `internal_blks=$((filesize / real_blksz))`

## Control Flow

The visible phases are driven by echo markers such as line 23 `echo "Format and mount"`, line 40 `echo "Create the original files"`, line 45 `echo "Compare files"`, line 49 `echo "CoW and unmount"`. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 13: `_begin_fstest auto quick clone fiemap`
- Line 19: `_require_scratch_reflink`
- Line 20: `_require_cp_reflink`
- Line 21: `_require_xfs_io_command "fiemap"`
- Line 23: `echo "Format and mount"`
- Line 24: `_scratch_mkfs > $seqres.full 2>&1`
- Line 25: `_scratch_mount >> $seqres.full 2>&1`
- Line 28: `mkdir $testdir`
- Line 41: `$XFS_IO_PROG -f -c "pwrite -S 0x61 -b $bufsize 0 $((filesize + 1))" $testdir/file1 >> $seqres.full`
- Line 42: `_cp_reflink $testdir/file1 $testdir/file2 >> $seqres.full`
- Line 43: `_scratch_cycle_mount`
- Line 46: `md5sum $testdir/file1 | _filter_scratch`
- Line 47: `md5sum $testdir/file2 | _filter_scratch`
- Line 56: `md5sum $testdir/file1 | _filter_scratch`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Cycle-mount calls force metadata and extent state through unmount/remount persistence before validation. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `clone`, `fiemap`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, and uses capability gates such as `_require_scratch_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "fiemap"`, `_require_fs_space $SCRATCH_MNT $((filesize / 1024 * 3 * 5 / 4))`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Reflink coverage is sensitive to extent alignment, delayed allocation, unwritten extents, and page-size dependent block geometry, so comparisons against check files are the main correctness guard.
- Extent-map output is formatted and filtered, but the test still depends on stable extent flags, logical block addressing, and filesystem support for the ioctl under test.

## Test Signals

The pass signal is filtered `md5sum` output, filtered extent-map output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
