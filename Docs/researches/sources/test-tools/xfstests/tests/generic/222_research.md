# sources/test-tools/xfstests/tests/generic/222

## Purpose

See what happens if we CoW blocks 2-4 of a page's worth of blocks when the second block is delalloc This test is dependent on the system page size, so we cannot use md5 in the golden output; we can only compare to a check file. It is registered with `_begin_fstest auto quick clone prealloc` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `222` plus `_begin_fstest auto quick clone prealloc`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`. Capability gates: `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 30: `pagesz=$(getconf PAGE_SIZE)`
- Line 31: `blksz=$((pagesz / 4))`
- Line 37: `testdir=$SCRATCH_MNT/test-$seq`
- Line 40: `real_blksz=$(_get_file_block_size $testdir)`
- Line 73: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 33 `echo "Format and mount"`, line 43 `echo "Create the original files"`, line 53 `echo "Compare files"`, line 57 `echo "CoW and unmount"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 20: `rm -rf $tmp.* $testdir`
- Line 27: `_require_scratch_reflink`
- Line 28: `_require_xfs_io_command "falloc"`
- Line 33: `echo "Format and mount"`
- Line 34: `_scratch_mkfs_blocksized $blksz > $seqres.full 2>&1`
- Line 35: `_scratch_mount >> $seqres.full 2>&1`
- Line 38: `mkdir $testdir`
- Line 44: `_pwrite_byte 0x61 0 $pagesz $testdir/file1 >> $seqres.full`
- Line 46: `$XFS_IO_PROG -f -c "truncate $pagesz" $testdir/file2 >> $seqres.full`
- Line 47: `$XFS_IO_PROG -f -c "truncate $pagesz" $testdir/file2.chk >> $seqres.full`
- Line 49: `_reflink_range $testdir/file1 $blksz $testdir/file2 $((blksz * 2)) $blksz >> $seqres.full`
- Line 50: `_pwrite_byte 0x61 $((blksz * 2)) $blksz $testdir/file2.chk >> $seqres.full`
- Line 51: `_scratch_cycle_mount`
- Line 70: `cmp -s $testdir/file2 $testdir/file2.chk || _fail "file2 and file2.chk don't match."`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Cycle-mount calls force metadata and extent state through unmount/remount persistence before validation. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `clone`, `prealloc`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, and uses capability gates such as `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Reflink coverage is sensitive to extent alignment, delayed allocation, unwritten extents, and page-size dependent block geometry, so comparisons against check files are the main correctness guard.
- Several checks can intentionally call `_notrun`; this is expected for unsupported geometry or feature combinations and should be distinguished from a failing assertion.

## Test Signals

The pass signal is byte-for-byte `cmp` checks against companion files, explicit `_fail` assertions. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
