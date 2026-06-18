# sources/test-tools/xfstests/tests/generic/728

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/728`. Test a bug where the NFS client wasn't sending a post-op GETATTR to the server after setting an xattr, resulting in `stat` reporting a stale ctime. It is registered with `_begin_fstest auto quick attr`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 41 source line(s).
- Harness registration: `_begin_fstest auto quick attr`.
- Imported common libraries: `./common/preamble`, `./common/attr`.
- Capability and skip gates: `_require_test`, `_require_attrs`.
- Local shell functions: `check_xattr_op`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `what=$1`
- `before_ctime=$(stat -c %z $TEST_DIR/testfile)`
- `after_ctime=$(stat -c %z $TEST_DIR/testfile)`

## Control Flow

- Capability gating runs first through `_require_test`, `_require_attrs`.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 39: echo "Silence is golden"`
- Key operational lines include:
- `line 27: before_ctime=$(stat -c %z $TEST_DIR/testfile)`
- `line 31: after_ctime=$(stat -c %z $TEST_DIR/testfile)`

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. Extended attributes are part of the persistent state being created, replayed, or verified. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick attr`, common helper libraries (`./common/preamble`, `./common/attr`), and the golden-output file `sources/test-tools/xfstests/tests/generic/728.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_test`, `_require_attrs`.

## Risks and Edge Cases

- Most failures should surface as unexpected output, nonzero helper status, or harness `_fail`/`_notrun` behavior.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 728; Silence is golden'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
