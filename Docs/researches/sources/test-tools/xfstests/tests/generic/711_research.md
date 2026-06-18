# sources/test-tools/xfstests/tests/generic/711

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/711`. Make sure that swapext won't touch a swap file. It is registered with `_begin_fstest auto quick swapext`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 46 source line(s).
- Harness registration: `_begin_fstest auto quick swapext`.
- Imported common libraries: `./common/preamble`, `./common/filter`.
- Capability and skip gates: `_require_xfs_io_command swapext`, `_require_test`.
- Local shell functions: `_cleanup`.
- External `$here/src` helpers: `$here/src/punch-alternating $dir/a`.
- Notable variables and constants:
- `dir=$TEST_DIR/test-$seq`

## Control Flow

- Capability gating runs first through `_require_xfs_io_command swapext`, `_require_test`.
- Key operational lines include:
- `line 30: $XFS_IO_PROG -f -c 'pwrite -S 0x58 0 32m -b 1m' -c fsync $dir/a >> $seqres.full`
- `line 32: $XFS_IO_PROG -f -c 'pwrite -S 0x58 0 32m -b 1m' -c fsync $dir/a >> $seqres.full`
- `line 35: $XFS_IO_PROG -f -c 'pwrite -S 0x59 0 32m -b 1m' $dir/b >> $seqres.full`
- `line 41: $XFS_IO_PROG -c "swapext $dir/b" $dir/a 2>&1 | \`

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick swapext`, common helper libraries (`./common/preamble`, `./common/filter`), and the golden-output file `sources/test-tools/xfstests/tests/generic/711.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_xfs_io_command swapext`, `_require_test`.

## Risks and Edge Cases

- Most failures should surface as unexpected output, nonzero helper status, or harness `_fail`/`_notrun` behavior.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 711; swapext: Text file busy'. Runtime pass/fail is primarily the command exit status plus golden-output comparison. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
