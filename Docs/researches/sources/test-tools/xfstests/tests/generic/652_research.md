# sources/test-tools/xfstests/tests/generic/652

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/652`. See what happens if we MMAP CoW blocks 2-4 of a page's worth of blocks when the second block is a unwritten block. (MMAP version of generic/216,217) This test is dependent on the system page size, so we cannot use md5 in the golden output; we can only compare to a check file. It is registered with `_begin_fstest auto quick clone prealloc mmap`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 68 source line(s).
- Harness registration: `_begin_fstest auto quick clone prealloc mmap`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/reflink`.
- Capability and skip gates: `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`.
- Local shell functions: none visible.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `pagesz=$(getconf PAGE_SIZE)`
- `blksz=$((pagesz / 4))`
- `testdir=$SCRATCH_MNT/test-$seq`
- `real_blksz=$(_get_file_block_size $testdir)`

## Control Flow

- Capability gating runs first through `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 25: echo "Format and mount"`
- `line 35: echo "Create the original files"`
- `line 51: echo "Compare files"`
- `line 55: echo "CoW and unmount"`
- `line 62: echo "Compare files"`
- Key operational lines include:
- `line 13: _begin_fstest auto quick clone prealloc mmap`
- `line 19: _require_scratch_reflink`
- `line 20: _require_xfs_io_command "falloc"`
- `line 26: _scratch_mkfs_blocksized $blksz > $seqres.full 2>&1`
- `line 27: _scratch_mount >> $seqres.full 2>&1`
- `line 38: $XFS_IO_PROG -f -c "truncate $pagesz" $testdir/file2 >> $seqres.full`
- `line 39: $XFS_IO_PROG -f -c "truncate $pagesz" $testdir/file2.chk >> $seqres.full`
- `line 41: $XFS_IO_PROG -f -c "falloc -k $blksz $blksz" $testdir/file2 >> $seqres.full`
- `line 44: $XFS_IO_PROG -f -c "falloc -k $((blksz * 3)) $blksz" $testdir/file2 >> $seqres.full`
- `line 47: _reflink_range $testdir/file1 $blksz $testdir/file2 $((blksz * 2)) $blksz >> $seqres.full`
- `line 49: _scratch_cycle_mount`
- `line 52: cmp -s $testdir/file1 $testdir/file2 && echo "file1 and file2 should not match."`
- `line 53: cmp -s $testdir/file2 $testdir/file2.chk || echo "file2 and file2.chk don't match."`
- `line 56: $XFS_IO_PROG -f -c "mmap 0 $pagesz" \`
- `line 58: $XFS_IO_PROG -f -c "mmap 0 $pagesz" \`
- `line 60: _scratch_cycle_mount`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick clone prealloc mmap`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/reflink`), and the golden-output file `sources/test-tools/xfstests/tests/generic/652.out` (6 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`.

## Risks and Edge Cases

- mmap/page-fault regressions are often race-prone and may manifest as hangs rather than clean command failures.
- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 6 line(s); its first visible signals are: 'QA output created by 652; Format and mount; Create the original files; Compare files; CoW and unmount'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, hang/race detection through background work, loops, or timeout windows, post-remount or failure-injection persistence checks. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
