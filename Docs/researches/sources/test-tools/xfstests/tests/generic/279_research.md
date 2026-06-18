# sources/test-tools/xfstests/tests/generic/279

## Purpose

Test mmap CoW behavior when the write temporarily fails. It is registered with `_begin_fstest auto quick clone eio mmap` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `279` plus `_begin_fstest auto quick clone eio mmap`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, `. ./common/dmerror`. Capability gates: `_require_scratch_reflink`, `_require_cp_reflink`, `_require_dm_target error`, `_require_fs_space $SCRATCH_MNT $((filesize / 1024 * 3 * 5 / 4))`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 34: `testdir=$SCRATCH_MNT/test-$seq`
- Line 37: `blksz=65536`
- Line 38: `nr=640`
- Line 39: `bufnr=128`
- Line 40: `filesize=$((blksz * nr))`
- Line 41: `bufsize=$((blksz * bufnr))`
- Line 79: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 29 `echo "Format and mount"`, line 45 `echo "Create the original files"`, line 51 `echo "Compare files"`, line 55 `echo "CoW and unmount"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 10: `_begin_fstest auto quick clone eio mmap`
- Line 17: `_dmerror_cleanup`
- Line 26: `_require_cp_reflink`
- Line 29: `echo "Format and mount"`
- Line 31: `_dmerror_init`
- Line 35: `mkdir $testdir`
- Line 47: `_cp_reflink $testdir/file1 $testdir/file2 >> $seqres.full`
- Line 49: `_dmerror_mount`
- Line 53: `md5sum $testdir/file2 | _filter_scratch`
- Line 56: `_scratch_sync`
- Line 61: `ulimit -c 0`
- Line 63: `-c "msync -s 0 $filesize" $testdir/file2 >> $seqres.full 2>&1`
- Line 67: `_dmerror_unmount`
- Line 76: `_repair_scratch_fs >> $seqres.full`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. It may also use `$TEST_DIR` for non-destructive helper programs or limit checks. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `clone`, `eio`, `mmap`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, `. ./common/dmerror`, and uses capability gates such as `_require_scratch_reflink`, `_require_cp_reflink`, `_require_dm_target error`, `_require_fs_space $SCRATCH_MNT $((filesize / 1024 * 3 * 5 / 4))`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Reflink coverage is sensitive to extent alignment, delayed allocation, unwritten extents, and page-size dependent block geometry, so comparisons against check files are the main correctness guard.
- mmap tests rely on page-cache writeback, timestamp granularity, and correct handling of dirty mappings across fsync, sync, or remount boundaries.

## Test Signals

The pass signal is filtered `md5sum` output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
