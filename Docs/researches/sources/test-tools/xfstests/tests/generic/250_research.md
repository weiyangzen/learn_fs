# sources/test-tools/xfstests/tests/generic/250

## Purpose

Create an unwritten extent, set up dm-error, try a DIO write, then make sure we can't read back old disk contents Disable the scratch rt device to avoid test failures relating to the rt bitmap consuming all the free space in our small data device. It is registered with `_begin_fstest auto quick prealloc rw eio` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `250` plus `_begin_fstest auto quick prealloc rw eio`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/dmerror`. Capability gates: `_require_scratch`, `_require_dm_target error`, `_require_xfs_io_command "falloc"`, `_require_odirect`, `_require_fs_space $SCRATCH_MNT $((filesize / 1024 * 5 / 4))`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 34: `fssize=$((196 * 1048576))`
- Line 43: `testdir=$SCRATCH_MNT/test-$seq`
- Line 46: `blksz=65536`
- Line 47: `nr=640`
- Line 48: `bufnr=128`
- Line 49: `filesize=$((blksz * nr))`
- Line 50: `bufsize=$((blksz * bufnr))`
- Line 81: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 35 `echo "Format and mount"`, line 54 `echo "Create the original files"`, line 59 `echo "Compare files"`, line 62 `echo "Write and unmount"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 17: `rm -rf $tmp.* $testdir`
- Line 25: `_require_scratch`
- Line 27: `_require_xfs_io_command "falloc"`
- Line 36: `$XFS_IO_PROG -d -c "pwrite -S 0x69 -b 1048576 0 $fssize" $SCRATCH_DEV >> $seqres.full`
- Line 38: `_dmerror_init`
- Line 40: `_dmerror_unmount`
- Line 44: `mkdir $testdir`
- Line 56: `_dmerror_unmount`
- Line 60: `md5sum $testdir/file2 | _filter_scratch`
- Line 63: `$XFS_IO_PROG -f -c "pwrite -S 0x63 $bufsize 1" $testdir/file2 >> $seqres.full`
- Line 65: `_dmerror_load_error_table`
- Line 68: `_dmerror_load_working_table`
- Line 70: `_dmerror_mount`
- Line 78: `_repair_scratch_fs >> $seqres.full`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `prealloc`, `rw`, `eio`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/dmerror`, and uses capability gates such as `_require_scratch`, `_require_dm_target error`, `_require_xfs_io_command "falloc"`, `_require_odirect`, `_require_fs_space $SCRATCH_MNT $((filesize / 1024 * 5 / 4))`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.

## Test Signals

The pass signal is filtered `md5sum` output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
