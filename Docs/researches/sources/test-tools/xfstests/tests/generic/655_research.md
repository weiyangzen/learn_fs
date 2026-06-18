# sources/test-tools/xfstests/tests/generic/655

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/655`. See what happens if we MMAP CoW blocks 2-4 of a page's worth of blocks when the surrounding blocks vary between unwritten/regular/delalloc/hole. (MMAP version of generic/229,238) This test is dependent on the system page size, so we cannot use md5 in the golden output; we can only compare to a check file. It is registered with `_begin_fstest auto quick clone fiemap prealloc mmap`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 131 source line(s).
- Harness registration: `_begin_fstest auto quick clone fiemap prealloc mmap`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/reflink`.
- Capability and skip gates: `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`, `_notrun "test requires delayed allocation writes"`, `_notrun "test requires delayed allocation writes"`.
- Local shell functions: `runtest`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `pagesz=$(getconf PAGE_SIZE)`
- `blksz=$((pagesz / 4))`
- `testdir=$SCRATCH_MNT/test-$seq`
- `real_blksz=$(_get_file_block_size $testdir)`
- `b2=$1`
- `b4=$2`
- `dir=$3`

## Control Flow

- Capability gating runs first through `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`, `_notrun "test requires delayed allocation writes"`, `_notrun "test requires delayed allocation writes"`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 26: echo "Format and mount"`
- `line 37: echo "runtest $1 $2"`
- `line 42: echo "Create the original files"`
- `line 79: echo "Compare files"`
- `line 83: echo "CoW and unmount"`
- `line 108: echo "Compare files"`
- Key operational lines include:
- `line 14: _begin_fstest auto quick clone fiemap prealloc mmap`
- `line 20: _require_scratch_reflink`
- `line 21: _require_xfs_io_command "falloc"`
- `line 27: _scratch_mkfs_blocksized $blksz > $seqres.full 2>&1`
- `line 28: _scratch_mount >> $seqres.full 2>&1`
- `line 46: $XFS_IO_PROG -f -c "truncate $pagesz" $dir/file2 >> $seqres.full`
- `line 47: $XFS_IO_PROG -f -c "truncate $pagesz" $dir/file2.chk >> $seqres.full`
- `line 55: $XFS_IO_PROG -f -c "falloc -k $blksz $blksz" $dir/file2 >> $seqres.full`
- `line 68: $XFS_IO_PROG -f -c "falloc -k $((blksz * 3)) $blksz" $dir/file2 >> $seqres.full`
- `line 75: _reflink_range $dir/file1 $blksz $dir/file2 $((blksz * 2)) $blksz >> $seqres.full`
- `line 77: _scratch_cycle_mount`
- `line 80: cmp -s $dir/file1 $dir/file2 && echo "file1 and file2 should not match."`
- `line 81: cmp -s $dir/file2 $dir/file2.chk || echo "file2 and file2.chk don't match."`
- `line 102: $XFS_IO_PROG -f -c "mmap 0 $pagesz" \`
- `line 104: $XFS_IO_PROG -f -c "mmap 0 $pagesz" \`
- `line 106: _scratch_cycle_mount`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick clone fiemap prealloc mmap`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/reflink`), and the golden-output file `sources/test-tools/xfstests/tests/generic/655.out` (62 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`, `_notrun "test requires delayed allocation writes"`, `_notrun "test requires delayed allocation writes"`.

## Risks and Edge Cases

- mmap/page-fault regressions are often race-prone and may manifest as hangs rather than clean command failures.
- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 62 line(s); its first visible signals are: 'QA output created by 655; Format and mount; runtest regular delalloc; Create the original files; Compare files'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, hang/race detection through background work, loops, or timeout windows, post-remount or failure-injection persistence checks. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
