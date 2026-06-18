# sources/test-tools/xfstests/tests/generic/736

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/736`. Test that on a fairly large directory if we keep renaming files while holding the directory open and doing readdir(3) calls, we don't end up in an infinite loop. It is registered with `_begin_fstest auto quick dir rename`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 36 source line(s).
- Harness registration: `_begin_fstest auto quick dir rename`.
- Imported common libraries: `./common/preamble`.
- Capability and skip gates: `_require_test`, `_require_test_program readdir-while-renames`, `_fixed_by_fs_commit btrfs 9b378f6ad48c "btrfs: fix infinite directory reads"`.
- Local shell functions: `_cleanup`.
- External `$here/src` helpers: `$here/src/readdir-while-renames $target_dir`.
- Notable variables and constants:
- `target_dir="$TEST_DIR/test-$seq"`

## Control Flow

- Capability gating runs first through `_require_test`, `_require_test_program readdir-while-renames`, `_fixed_by_fs_commit btrfs 9b378f6ad48c "btrfs: fix infinite directory reads"`.
- User-visible phase markers include:
- `line 34: echo "Silence is golden"`

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick dir rename`, common helper libraries (`./common/preamble`), and the golden-output file `sources/test-tools/xfstests/tests/generic/736.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_test`, `_require_test_program readdir-while-renames`, `_fixed_by_fs_commit btrfs 9b378f6ad48c "btrfs: fix infinite directory reads"`.

## Risks and Edge Cases

- Directory mutation and rename races depend on dentry-cache timing and may need repeated attempts to expose regressions.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 736; Silence is golden'. Runtime pass/fail is primarily the command exit status plus golden-output comparison. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
