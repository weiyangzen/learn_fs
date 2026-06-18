# sources/test-tools/xfstests/tests/generic/713

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/713`. Test exchangerange between ranges of two different files. It is registered with `_begin_fstest auto quick fiexchange`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 99 source line(s).
- Harness registration: `_begin_fstest auto quick fiexchange`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/reflink`.
- Capability and skip gates: `_require_xfs_io_command exchangerange ' -s 64k -l 64k'`, `_require_xfs_io_command "falloc"`, `_require_test`, `_require_congruent_file_oplen $TEST_DIR $blksz`.
- Local shell functions: `_cleanup`, `filesnap`, `test_exchangerange_once`, `test_exchangerange_two`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `dir=$TEST_DIR/test-$seq`
- `blksz=65536`
- `nrblks=57`

## Control Flow

- Capability gating runs first through `_require_xfs_io_command exchangerange ' -s 64k -l 64k'`, `_require_xfs_io_command "falloc"`, `_require_test`, `_require_congruent_file_oplen $TEST_DIR $blksz`.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 28: echo "$1"`
- `line 42: echo`
- Key operational lines include:
- `line 23: _require_xfs_io_command exchangerange ' -s 64k -l 64k'`
- `line 24: _require_xfs_io_command "falloc"`
- `line 30: md5sum $2 $3 | _filter_test_dir`
- `line 32: md5sum $2 | _filter_test_dir`
- `line 36: test_exchangerange_once() {`
- `line 37: filesnap "$1: before exchangerange" $dir/$3 $dir/$4`
- `line 38: $XFS_IO_PROG -c "exchangerange $2 $dir/$3" $dir/$4`
- `line 39: filesnap "$1: after exchangerange" $dir/$3 $dir/$4`
- `line 45: test_exchangerange_two() {`
- `line 47: test_exchangerange_once "$*: samerange" \`
- `line 51: test_exchangerange_once "$*: diffrange" \`
- `line 55: test_exchangerange_once "$*: overlap" \`
- `line 69: test_exchangerange_two "simple"`
- `line 75: test_exchangerange_once "unalignedeof" "" a b`
- `line 81: test_exchangerange_two "rainbow"`
- `line 85: $XFS_IO_PROG -f -c "pwrite -S 0x58 0 $((blksz * nrblks))" \`

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick fiexchange`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/reflink`), and the golden-output file `sources/test-tools/xfstests/tests/generic/713.out` (86 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_xfs_io_command exchangerange ' -s 64k -l 64k'`, `_require_xfs_io_command "falloc"`, `_require_test`, `_require_congruent_file_oplen $TEST_DIR $blksz`.

## Risks and Edge Cases

- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 86 line(s); its first visible signals are: 'QA output created by 713; simple: samerange: before exchangerange; db85d578204631f2b4eb1e73974253c2  TEST_DIR/test-713/b; d0425612f15c6071022cf7127620f63d  TEST_DIR/test-713/a; simple: samerange: after exchangerange'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, xfstests output filters. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
