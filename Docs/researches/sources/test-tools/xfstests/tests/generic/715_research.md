# sources/test-tools/xfstests/tests/generic/715

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/715`. Test exchangerange between two files of unlike size. It is registered with `_begin_fstest auto quick fiexchange`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 77 source line(s).
- Harness registration: `_begin_fstest auto quick fiexchange`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/reflink`.
- Capability and skip gates: `_require_xfs_io_command exchangerange ' -s 64k -l 64k'`, `_require_test`.
- Local shell functions: `_cleanup`, `filesnap`, `test_exchangerange_once`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `len=""`
- `len="-l $((blksz * len))"`
- `cmd="exchangerange -s $((blksz * a_off)) -d $((blksz * b_off)) $len $dir/a"`
- `dir=$TEST_DIR/test-$seq`
- `blksz=65536`

## Control Flow

- Capability gating runs first through `_require_xfs_io_command exchangerange ' -s 64k -l 64k'`, `_require_test`.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 27: echo "$1"`
- `line 56: echo "$cmd" >> $seqres.full`
- `line 62: echo`
- Key operational lines include:
- `line 23: _require_xfs_io_command exchangerange ' -s 64k -l 64k'`
- `line 29: md5sum $2 $3 | _filter_test_dir`
- `line 31: md5sum $2 | _filter_test_dir`
- `line 35: test_exchangerange_once() {`
- `line 53: filesnap "$tag: before exchangerange" $dir/a $dir/b`
- `line 55: cmd="exchangerange -s $((blksz * a_off)) -d $((blksz * b_off)) $len $dir/a"`
- `line 57: $XFS_IO_PROG -c "$cmd" $dir/b`
- `line 58: filesnap "$tag: after exchangerange" $dir/a $dir/b`
- `line 69: test_exchangerange_once "last 5 blocks" 27 37 22 32 5`
- `line 71: test_exchangerange_once "whole file to eof" 27 37 0 0 EOF`
- `line 73: test_exchangerange_once "blocks 30-40" 27 37 30 30 10`

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick fiexchange`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/reflink`), and the golden-output file `sources/test-tools/xfstests/tests/generic/715.out` (32 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_xfs_io_command exchangerange ' -s 64k -l 64k'`, `_require_test`.

## Risks and Edge Cases

- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 32 line(s); its first visible signals are: 'QA output created by 715; last 5 blocks: before exchangerange; 207ea56e0ccbf50d38fd3a2d842aa170  TEST_DIR/test-715/a; eb58941d31f5be1e4e22df8c536dd490  TEST_DIR/test-715/b; last 5 blocks: after exchangerange'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, xfstests output filters. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
