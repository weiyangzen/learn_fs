# sources/test-tools/xfstests/tests/generic/714

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/714`. Test exchangerange between ranges of two different files, when one of the files is shared. It is registered with `_begin_fstest auto quick fiexchange`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 115 source line(s).
- Harness registration: `_begin_fstest auto quick fiexchange`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/reflink`.
- Capability and skip gates: `_require_xfs_io_command exchangerange`, `_require_xfs_io_command "falloc"`, `_require_test_reflink`, `_require_congruent_file_oplen $TEST_DIR $blksz`.
- Local shell functions: `_cleanup`, `filesnap`, `test_exchangerange_once`, `test_exchangerange_two`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `dir=$TEST_DIR/test-$seq`
- `blksz=65536`
- `nrblks=57`

## Control Flow

- Capability gating runs first through `_require_xfs_io_command exchangerange`, `_require_xfs_io_command "falloc"`, `_require_test_reflink`, `_require_congruent_file_oplen $TEST_DIR $blksz`.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 29: echo "$1"`
- `line 43: echo`
- `line 60: echo "overwrite A and B entirely"`
- `line 67: echo`
- `line 106: echo "overwrite C entirely"`
- Key operational lines include:
- `line 24: _require_xfs_io_command exchangerange`
- `line 25: _require_xfs_io_command "falloc"`
- `line 26: _require_test_reflink`
- `line 31: md5sum $2 $3 | _filter_test_dir`
- `line 33: md5sum $2 | _filter_test_dir`
- `line 37: test_exchangerange_once() {`
- `line 38: filesnap "$1: before exchangerange" $dir/$3 $dir/$4`
- `line 39: $XFS_IO_PROG -c "exchangerange $2 $dir/$3" $dir/$4`
- `line 40: filesnap "$1: after exchangerange" $dir/$3 $dir/$4`
- `line 46: test_exchangerange_two() {`
- `line 48: test_exchangerange_once "$*: samerange" \`
- `line 52: test_exchangerange_once "$*: diffrange" \`
- `line 56: test_exchangerange_once "$*: overlap" \`
- `line 61: md5sum $dir/sharea | _filter_test_dir`
- `line 62: $XFS_IO_PROG -c "pwrite -S 0x60 0 $((blksz * nrblks))" $dir/a >> $seqres.full`
- `line 63: $XFS_IO_PROG -c "pwrite -S 0x60 0 $((blksz * nrblks))" $dir/b >> $seqres.full`

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick fiexchange`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/reflink`), and the golden-output file `sources/test-tools/xfstests/tests/generic/714.out` (90 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_xfs_io_command exchangerange`, `_require_xfs_io_command "falloc"`, `_require_test_reflink`, `_require_congruent_file_oplen $TEST_DIR $blksz`.

## Risks and Edge Cases

- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 90 line(s); its first visible signals are: 'QA output created by 714; simple: samerange: before exchangerange; db85d578204631f2b4eb1e73974253c2  TEST_DIR/test-714/b; d0425612f15c6071022cf7127620f63d  TEST_DIR/test-714/a; simple: samerange: after exchangerange'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, xfstests output filters. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
