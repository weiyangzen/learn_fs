# sources/test-tools/xfstests/tests/generic/720

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/720`. Stress testing with a lot of extents. It is registered with `_begin_fstest auto quick fiexchange`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 57 source line(s).
- Harness registration: `_begin_fstest auto quick fiexchange`.
- Imported common libraries: `./common/preamble`, `./common/filter`.
- Capability and skip gates: `_require_xfs_io_command exchangerange`, `_require_test_program punch-alternating`, `_require_test`, `_require_fs_space $TEST_DIR $(( (2 * blksz * nrblks) / 1024 ))`.
- Local shell functions: `_cleanup`.
- External `$here/src` helpers: `$here/src/punch-alternating $dir/a`, `$here/src/punch-alternating -o 1 $dir/b`.
- Notable variables and constants:
- `dir=$TEST_DIR/test-$seq`
- `blksz=$(_get_file_block_size $TEST_DIR)`
- `nrblks=$((LOAD_FACTOR * 100000))`
- `md5_a="$(md5sum < $dir/a)"`
- `md5_b="$(md5sum < $dir/b)"`

## Control Flow

- Capability gating runs first through `_require_xfs_io_command exchangerange`, `_require_test_program punch-alternating`, `_require_test`, `_require_fs_space $TEST_DIR $(( (2 * blksz * nrblks) / 1024 ))`.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 47: echo "md5_a=$md5_a" >> $seqres.full`
- `line 48: echo "md5_b=$md5_b" >> $seqres.full`
- `line 54: echo "Silence is golden!"`
- Key operational lines include:
- `line 22: _require_xfs_io_command exchangerange`
- `line 41: md5_a="$(md5sum < $dir/a)"`
- `line 42: md5_b="$(md5sum < $dir/b)"`
- `line 44: $XFS_IO_PROG -c "exchangerange $dir/b" $dir/a`
- `line 49: md5sum $dir/a $dir/b >> $seqres.full`
- `line 51: test "$(md5sum < $dir/b)" = "$md5_a" || echo "file b does not match former a"`
- `line 52: test "$(md5sum < $dir/a)" = "$md5_b" || echo "file a does not match former b"`

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick fiexchange`, common helper libraries (`./common/preamble`, `./common/filter`), and the golden-output file `sources/test-tools/xfstests/tests/generic/720.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_xfs_io_command exchangerange`, `_require_test_program punch-alternating`, `_require_test`, `_require_fs_space $TEST_DIR $(( (2 * blksz * nrblks) / 1024 ))`.

## Risks and Edge Cases

- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 720; Silence is golden!'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
