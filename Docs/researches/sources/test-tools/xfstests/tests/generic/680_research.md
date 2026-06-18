# sources/test-tools/xfstests/tests/generic/680

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/680`. Test for the Dirty Pipe vulnerability (CVE-2022-0847) caused by an uninitialized "pipe_buffer.flags" variable, which fixed by: 9d2231c5d74e ("lib/iov_iter: initialize "flags" in new pipe_buffer") It is registered with `_begin_fstest auto quick`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 46 source line(s).
- Harness registration: `_begin_fstest auto quick`.
- Imported common libraries: `./common/preamble`.
- Capability and skip gates: `_require_test`, `_require_user`, `_require_chmod`, `_require_test_program "splice2pipe"`.
- Local shell functions: none visible.
- External `$here/src` helpers: `$here/src/splice2pipe $localfile 1 "AAAAAAAABBBBBBBB"`, `cp $here/src/splice2pipe $tmp.splice2pipe`.
- Notable variables and constants:
- `localfile=$TEST_DIR/testfile.$seq`

## Control Flow

- Capability gating runs first through `_require_test`, `_require_user`, `_require_chmod`, `_require_test_program "splice2pipe"`.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 27: echo "Test privileged user:"`
- `line 40: echo "Test unprivileged user:"`
- Key operational lines include:
- `line 24: $XFS_IO_PROG -f -t -c "pwrite 0 4k -S 0xff" $localfile >> $seqres.full 2>&1`
- `line 30: _hexdump $localfile`
- `line 34: $XFS_IO_PROG -f -t -c "pwrite 0 4k -S 0xff" $localfile >> $seqres.full 2>&1`
- `line 42: _hexdump $localfile`

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick`, common helper libraries (`./common/preamble`), and the golden-output file `sources/test-tools/xfstests/tests/generic/680.out` (9 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_test`, `_require_user`, `_require_chmod`, `_require_test_program "splice2pipe"`.

## Risks and Edge Cases

- Most failures should surface as unexpected output, nonzero helper status, or harness `_fail`/`_notrun` behavior.

## Test Signals

The paired `.out` file has 9 line(s); its first visible signals are: 'QA output created by 680; Test privileged user:; 000000 ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff  >................<; *; 001000'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
