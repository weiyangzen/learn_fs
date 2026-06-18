# sources/test-tools/xfstests/tests/generic/718

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/718`. Make sure exchangerange honors RLIMIT_FSIZE. It is registered with `_begin_fstest auto quick fiexchange`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 47 source line(s).
- Harness registration: `_begin_fstest auto quick fiexchange`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/reflink`.
- Capability and skip gates: `_require_xfs_io_command exchangerange`, `_require_test`.
- Local shell functions: `_cleanup`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `dir=$TEST_DIR/test-$seq`
- `blksz=65536`
- `nrblks=64`

## Control Flow

- Capability gating runs first through `_require_xfs_io_command exchangerange`, `_require_test`.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- Key operational lines include:
- `line 23: _require_xfs_io_command exchangerange`
- `line 35: md5sum $dir/a $dir/b | _filter_test_dir`
- `line 42: $XFS_IO_PROG -c "exchangerange $dir/b" $dir/a`
- `line 43: md5sum $dir/a $dir/b | _filter_test_dir`

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick fiexchange`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/reflink`), and the golden-output file `sources/test-tools/xfstests/tests/generic/718.out` (6 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_xfs_io_command exchangerange`, `_require_test`.

## Risks and Edge Cases

- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 6 line(s); its first visible signals are: 'QA output created by 718; d712f003e9d467e063cda1baf319b928  TEST_DIR/test-718/a; 901e136269b8d283d311697b7c6dc1f2  TEST_DIR/test-718/b; exchangerange: Invalid argument; d712f003e9d467e063cda1baf319b928  TEST_DIR/test-718/a'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, xfstests output filters. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
