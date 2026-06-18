# sources/test-tools/xfstests/tests/generic/734

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/734`. This is a regression test for the kernel commit noted below. The stale memory exposure can be exploited by creating a file with shared blocks, evicting the page cache for that file, and then funshareing at least one memory page's worth of data. iomap will mark the page uptodate and dirty without ever reading the ondisk contents. It is registered with `_begin_fstest auto quick unshare clone`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 85 source line(s).
- Harness registration: `_begin_fstest auto quick unshare clone`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/reflink`.
- Capability and skip gates: `_fixed_by_git_commit kernel 35d30c9cf127 "iomap: don't skip reading in !uptodate folios when unsharing a range"`, `_require_test_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "funshare"`.
- Local shell functions: `_cleanup`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `testdir=$TEST_DIR/test-$seq`
- `pagesz=$(_get_page_size)`
- `alloc_unit=$(_get_file_block_size $TEST_DIR)`
- `filesz=$(( ( (4 * pagesz) + alloc_unit - 1) / alloc_unit * alloc_unit))`

## Control Flow

- Capability gating runs first through `_fixed_by_git_commit kernel 35d30c9cf127 "iomap: don't skip reading in !uptodate folios when unsharing a range"`, `_require_test_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "funshare"`.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 44: echo "Create the original file and a clone"`
- `line 54: echo "Funshare at least one pagecache page"`
- `line 59: echo "Check contents"`
- `line 63: echo "file2.chk does not match file2"`
- `line 65: echo "file2.chk contents" >> $seqres.full`
- `line 67: echo "file2 contents" >> $seqres.full`
- `line 69: echo "end bad contents" >> $seqres.full`
- `line 74: echo "file2.chk does not match file3"`
- Key operational lines include:
- `line 30: _require_test_reflink`
- `line 31: _require_cp_reflink`
- `line 47: _cp_reflink $testdir/file1 $testdir/file2`
- `line 48: _cp_reflink $testdir/file1 $testdir/file3`
- `line 55: $XFS_IO_PROG -c "funshare 0 $filesz" $testdir/file2`
- `line 56: $XFS_IO_PROG -c "funshare 0 $filesz" $testdir/file3`
- `line 62: if ! cmp -s $testdir/file2.chk $testdir/file2; then`
- `line 73: if ! cmp -s $testdir/file2.chk $testdir/file3; then`

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick unshare clone`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/reflink`), and the golden-output file `sources/test-tools/xfstests/tests/generic/734.out` (4 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_fixed_by_git_commit kernel 35d30c9cf127 "iomap: don't skip reading in !uptodate folios when unsharing a range"`, `_require_test_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "funshare"`.

## Risks and Edge Cases

- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 4 line(s); its first visible signals are: 'QA output created by 734; Create the original file and a clone; Funshare at least one pagecache page; Check contents'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
