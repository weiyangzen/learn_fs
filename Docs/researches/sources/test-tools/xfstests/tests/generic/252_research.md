# sources/test-tools/xfstests/tests/generic/252

## Purpose

Create an unwritten extent, set up dm-error, try an AIO DIO write, then make sure we can't read back old disk contents Disable the scratch rt device to avoid test failures relating to the rt bitmap consuming all the free space in our small data device. It is registered with `_begin_fstest auto quick prealloc rw eio` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `252` plus `_begin_fstest auto quick prealloc rw eio`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/dmerror`. Capability gates: `_require_scratch`, `_require_dm_target error`, `_require_xfs_io_command "falloc"`, `_require_aiodio "aiocp"`, `_require_fs_space $SCRATCH_MNT $((filesize / 1024 * 5 / 4))`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 29: `AIO_TEST="$here/src/aio-dio-regress/aiocp"`
- Line 35: `fssize=$((196 * 1048576))`
- Line 44: `testdir=$SCRATCH_MNT/test-$seq`
- Line 47: `blksz=65536`
- Line 48: `nr=640`
- Line 49: `bufnr=128`
- Line 50: `filesize=$((blksz * nr))`
- Line 51: `bufsize=$((blksz * bufnr))`

## Control Flow

The visible phases are driven by echo markers such as line 36 `echo "Format and mount"`, line 56 `echo "Create the original files"`, line 61 `echo "Compare files"`, line 64 `echo "CoW and unmount"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 17: `rm -rf $tmp.* $testdir $TEST_DIR/moo`
- Line 25: `_require_scratch`
- Line 27: `_require_xfs_io_command "falloc"`
- Line 37: `$XFS_IO_PROG -d -c "pwrite -S 0x69 -b 1048576 0 $fssize" $SCRATCH_DEV >> $seqres.full`
- Line 39: `_dmerror_init`
- Line 41: `_dmerror_unmount`
- Line 45: `mkdir $testdir`
- Line 58: `_dmerror_unmount`
- Line 62: `md5sum $testdir/file2 | _filter_scratch`
- Line 65: `$XFS_IO_PROG -f -c "pwrite -S 0x63 $bufsize 1" $testdir/file2 >> $seqres.full`
- Line 67: `_scratch_sync`
- Line 70: `_filter_flakey_EIO "write missed bytes expect 8388608 got 0"`
- Line 72: `_dmerror_unmount`
- Line 81: `_repair_scratch_fs >> $seqres.full`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. It may also use `$TEST_DIR` for non-destructive helper programs or limit checks. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `prealloc`, `rw`, `eio`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/dmerror`, and uses capability gates such as `_require_scratch`, `_require_dm_target error`, `_require_xfs_io_command "falloc"`, `_require_aiodio "aiocp"`, `_require_fs_space $SCRATCH_MNT $((filesize / 1024 * 5 / 4))`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.
- Crash-recovery tests require dm-flakey behavior and metadata journaling; failures can appear as lost directory entries, stale content, or mount-time recovery errors.

## Test Signals

The pass signal is filtered `md5sum` output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
