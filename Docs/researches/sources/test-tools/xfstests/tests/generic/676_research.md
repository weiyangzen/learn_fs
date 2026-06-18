# sources/test-tools/xfstests/tests/generic/676

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/676`. Test that filesystem properly handles seeking in directory both to valid and invalid positions. This is a regression test for a48fc69fe658 ("udf: Fix crash after seekdir") It is registered with `_begin_fstest auto quick`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 39 source line(s).
- Harness registration: `_begin_fstest auto quick`.
- Imported common libraries: `./common/preamble`.
- Capability and skip gates: `_require_test`, `_require_test_program "t_readdir_3"`.
- Local shell functions: `_cleanup`.
- External `$here/src` helpers: `$here/src/t_readdir_3 $dir $files $seed >> $seqres.full`.
- Notable variables and constants:
- `dir=$TEST_DIR/$seq-dir`
- `files=4000`
- `seed=$RANDOM`

## Control Flow

- Capability gating runs first through `_require_test`, `_require_test_program "t_readdir_3"`.
- User-visible phase markers include:
- `line 34: echo "Using seed $seed" >> $seqres.full`

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick`, common helper libraries (`./common/preamble`), and the golden-output file `sources/test-tools/xfstests/tests/generic/676.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_test`, `_require_test_program "t_readdir_3"`.

## Risks and Edge Cases

- Most failures should surface as unexpected output, nonzero helper status, or harness `_fail`/`_notrun` behavior.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 676; All tests passed'. Runtime pass/fail is primarily the command exit status plus golden-output comparison. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
