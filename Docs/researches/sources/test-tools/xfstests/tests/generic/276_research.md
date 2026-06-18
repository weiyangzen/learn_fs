# sources/test-tools/xfstests/tests/generic/276

## Purpose

Test DIO CoW behavior when the write temporarily fails and we unmount. It is registered with `_begin_fstest auto quick clone eio` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `276` plus `_begin_fstest auto quick clone eio`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, `. ./common/dmerror`. Capability gates: `_require_scratch_reflink`, `_require_cp_reflink`, `_require_dm_target error`, `_require_odirect`, `_require_fs_space $SCRATCH_MNT $((filesize / 1024 * 3 * 5 / 4))`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 35: `testdir=$SCRATCH_MNT/test-$seq`
- Line 38: `blksz=65536`
- Line 39: `nr=640`
- Line 40: `bufnr=128`
- Line 41: `filesize=$((blksz * nr))`
- Line 42: `bufsize=$((blksz * bufnr))`
- Line 75: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 30 `echo "Format and mount"`, line 46 `echo "Create the original files"`, line 52 `echo "Compare files"`, line 56 `echo "CoW and unmount"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 16: `rm -rf $tmp.*`
- Line 25: `_require_scratch_reflink`
- Line 27: `_require_dm_target error`
- Line 31: `_scratch_mkfs > $seqres.full 2>&1`
- Line 33: `_dmerror_mount >> $seqres.full 2>&1`
- Line 47: `$XFS_IO_PROG -f -c "pwrite -S 0x61 -b $bufsize 0 $filesize" $testdir/file1 >> $seqres.full`
- Line 49: `_dmerror_unmount`
- Line 53: `md5sum $testdir/file1 | _filter_scratch`
- Line 56: `echo "CoW and unmount"`
- Line 58: `_dmerror_load_error_table`
- Line 61: `_dmerror_load_working_table`
- Line 63: `_dmerror_unmount`
- Line 67: `md5sum $testdir/file1 | _filter_scratch`
- Line 72: `_repair_scratch_fs >> $seqres.full`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `clone`, `eio`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, `. ./common/dmerror`, and uses capability gates such as `_require_scratch_reflink`, `_require_cp_reflink`, `_require_dm_target error`, `_require_odirect`, `_require_fs_space $SCRATCH_MNT $((filesize / 1024 * 3 * 5 / 4))`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Reflink coverage is sensitive to extent alignment, delayed allocation, unwritten extents, and page-size dependent block geometry, so comparisons against check files are the main correctness guard.
- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.

## Test Signals

The pass signal is filtered `md5sum` output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
