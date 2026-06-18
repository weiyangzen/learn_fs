# sources/test-tools/xfstests/tests/generic/706

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/706`. Test that seeking for data on a 1 byte file works correctly, the returned offset should be 0 if the start offset is 0. It is registered with `_begin_fstest auto quick seek`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 34 source line(s).
- Harness registration: `_begin_fstest auto quick seek`.
- Imported common libraries: `./common/preamble`.
- Capability and skip gates: `_fixed_by_fs_commit btrfs 2f2e84ca6066 "btrfs: fix off-by-one in delalloc search during lseek"`, `_require_test`, `_require_seek_data_hole`, `_require_test_program "seek_sanity_test"`.
- Local shell functions: `_cleanup`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `test_file=$TEST_DIR/seek_sanity_testfile.$seq`

## Control Flow

- Capability gating runs first through `_fixed_by_fs_commit btrfs 2f2e84ca6066 "btrfs: fix off-by-one in delalloc search during lseek"`, `_require_test`, `_require_seek_data_hole`, `_require_test_program "seek_sanity_test"`.
- User-visible phase markers include:
- `line 32: echo "Silence is golden"`

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick seek`, common helper libraries (`./common/preamble`), and the golden-output file `sources/test-tools/xfstests/tests/generic/706.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_fixed_by_fs_commit btrfs 2f2e84ca6066 "btrfs: fix off-by-one in delalloc search during lseek"`, `_require_test`, `_require_seek_data_hole`, `_require_test_program "seek_sanity_test"`.

## Risks and Edge Cases

- Most failures should surface as unexpected output, nonzero helper status, or harness `_fail`/`_notrun` behavior.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 706; Silence is golden'. Runtime pass/fail is primarily the command exit status plus golden-output comparison. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
