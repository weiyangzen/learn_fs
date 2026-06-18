# sources/test-tools/xfstests/tests/generic/287

## Purpose

Ensuring that copy on write in directio mode to the source file when the CoW range covers regular unshared and regular shared blocks - Create two files - Reflink the odd blocks of the first file into the second file - dio CoW the first file across the halfway mark, starting with the regular extent - Check that the files are now different where we say they're different. It is registered with `_begin_fstest auto quick clone prealloc` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `287` plus `_begin_fstest auto quick clone prealloc`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`. Capability gates: `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`, `_require_odirect`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 30: `testdir=$SCRATCH_MNT/test-$seq`
- Line 34: `blksz=65536`
- Line 36: `nr=64`
- Line 37: `filesize=$((blksz * nr))`
- Line 47: `cowoff=$((filesize / 4))`
- Line 48: `cowsz=$((filesize / 2))`
- Line 59: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 26 `echo "Format and mount"`, line 33 `echo "Create the original files"`, line 41 `echo "Compare files"`, line 46 `echo "CoW across the transition"`. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 22: `_require_scratch_reflink`
- Line 23: `_require_xfs_io_command "falloc"`
- Line 26: `echo "Format and mount"`
- Line 27: `_scratch_mkfs > $seqres.full 2>&1`
- Line 28: `_scratch_mount >> $seqres.full 2>&1`
- Line 31: `mkdir $testdir`
- Line 38: `_sweave_reflink_regular $blksz $nr $testdir/file1 $testdir/file3 >> $seqres.full`
- Line 39: `_scratch_cycle_mount`
- Line 42: `md5sum $testdir/file1 | _filter_scratch`
- Line 43: `md5sum $testdir/file3 | _filter_scratch`
- Line 44: `md5sum $testdir/file1.chk | _filter_scratch`
- Line 49: `$XFS_IO_PROG -d -f -c "pwrite -S 0x63 -b $cowsz $cowoff $cowsz" $testdir/file1 >> $seqres.full`
- Line 50: `_pwrite_byte 0x63 $cowoff $cowsz $testdir/file1.chk >> $seqres.full`
- Line 56: `md5sum $testdir/file1.chk | _filter_scratch`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Cycle-mount calls force metadata and extent state through unmount/remount persistence before validation. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `clone`, `prealloc`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, and uses capability gates such as `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`, `_require_odirect`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Reflink coverage is sensitive to extent alignment, delayed allocation, unwritten extents, and page-size dependent block geometry, so comparisons against check files are the main correctness guard.
- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.

## Test Signals

The pass signal is filtered `md5sum` output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
