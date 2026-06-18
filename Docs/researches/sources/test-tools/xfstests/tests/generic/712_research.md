# sources/test-tools/xfstests/tests/generic/712

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/712`. Make sure that exchangerange modifies ctime and not mtime of the file. It is registered with `_begin_fstest auto quick fiexchange`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 57 source line(s).
- Harness registration: `_begin_fstest auto quick fiexchange`.
- Imported common libraries: `./common/preamble`, `./common/filter`.
- Capability and skip gates: `_require_test_program punch-alternating`, `_require_xfs_io_command exchangerange`, `_require_test`.
- Local shell functions: `_cleanup`.
- External `$here/src` helpers: `$here/src/punch-alternating $dir/a`.
- Notable variables and constants:
- `dir=$TEST_DIR/test-$seq`
- `old_mtime="$(echo $(stat -c '%y' $dir/a $dir/b))"`
- `old_ctime="$(echo $(stat -c '%z' $dir/a $dir/b))"`
- `new_mtime="$(echo $(stat -c '%y' $dir/a $dir/b))"`
- `new_ctime="$(echo $(stat -c '%z' $dir/a $dir/b))"`

## Control Flow

- Capability gating runs first through `_require_test_program punch-alternating`, `_require_xfs_io_command exchangerange`, `_require_test`.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 35: echo before >> $seqres.full`
- `line 45: echo after >> $seqres.full`
- `line 55: echo Silence is golden.`
- Key operational lines include:
- `line 23: _require_xfs_io_command exchangerange`
- `line 30: $XFS_IO_PROG -f -c 'pwrite -S 0x58 0 256k -b 1m' $dir/a >> $seqres.full`
- `line 32: $XFS_IO_PROG -f -c 'pwrite -S 0x59 0 256k -b 1m' $dir/b >> $seqres.full`
- `line 36: md5sum $dir/a $dir/b >> $seqres.full`
- `line 37: old_mtime="$(echo $(stat -c '%y' $dir/a $dir/b))"`
- `line 38: old_ctime="$(echo $(stat -c '%z' $dir/a $dir/b))"`
- `line 39: stat -c '%y %Y %z %Z' $dir/a $dir/b >> $seqres.full`
- `line 42: $XFS_IO_PROG -c "exchangerange $dir/b" $dir/a`
- `line 46: md5sum $dir/a $dir/b >> $seqres.full`
- `line 47: new_mtime="$(echo $(stat -c '%y' $dir/a $dir/b))"`
- `line 48: new_ctime="$(echo $(stat -c '%z' $dir/a $dir/b))"`
- `line 49: stat -c '%y %Y %z %Z' $dir/a $dir/b >> $seqres.full`

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick fiexchange`, common helper libraries (`./common/preamble`, `./common/filter`), and the golden-output file `sources/test-tools/xfstests/tests/generic/712.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_test_program punch-alternating`, `_require_xfs_io_command exchangerange`, `_require_test`.

## Risks and Edge Cases

- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 712; Silence is golden.'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
