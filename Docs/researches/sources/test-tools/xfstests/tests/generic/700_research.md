# sources/test-tools/xfstests/tests/generic/700

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/700`. Verify selinux label can be kept after RENAME_WHITEOUT. This is a regression test for: 70b589a37e1a ("xfs: add selinux labels to whiteout inodes") It is registered with `_begin_fstest auto quick rename attr whiteout`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 62 source line(s).
- Harness registration: `_begin_fstest auto quick rename attr whiteout`.
- Imported common libraries: `./common/preamble`, `./common/attr`, `./common/renameat2`.
- Capability and skip gates: `_require_scratch`, `_require_attrs`, `_require_renameat2 whiteout`, `_fixed_by_fs_commit xfs 70b589a37e1a "xfs: add selinux labels to whiteout inodes"`, `_notrun "Require selinux to be enabled"`.
- Local shell functions: `get_selinux_label`.
- External `$here/src` helpers: `$here/src/renameat2 -w $SCRATCH_MNT/f1 $SCRATCH_MNT/f2`.
- Notable variables and constants:
- `label=$(_getfattr --absolute-names -n security.selinux $@ | sed -n 's/security.selinux=\"\(.*\)\"/\1/p')`
- `label1=$(get_selinux_label $SCRATCH_MNT/f1)`
- `label2=$(get_selinux_label $SCRATCH_MNT/f2)`

## Control Flow

- Capability gating runs first through `_require_scratch`, `_require_attrs`, `_require_renameat2 whiteout`, `_fixed_by_fs_commit xfs 70b589a37e1a "xfs: add selinux labels to whiteout inodes"`, `_notrun "Require selinux to be enabled"`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- User-visible phase markers include:
- `line 33: echo $label`
- `line 47: echo "Before RENAME_WHITEOUT" >> $seqres.full`
- `line 51: echo "After RENAME_WHITEOUT" >> $seqres.full`
- `line 56: echo "$label1 != $label2"`
- `line 59: echo "Silence is golden"`
- Key operational lines include:
- `line 20: _require_renameat2 whiteout`
- `line 29: label=$(_getfattr --absolute-names -n security.selinux $@ | sed -n 's/security.selinux=\"\(.*\)\"/\1/p')`
- `line 36: _scratch_mkfs >> $seqres.full 2>&1`
- `line 44: _scratch_mount`
- `line 50: $here/src/renameat2 -w $SCRATCH_MNT/f1 $SCRATCH_MNT/f2`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Extended attributes are part of the persistent state being created, replayed, or verified. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick rename attr whiteout`, common helper libraries (`./common/preamble`, `./common/attr`, `./common/renameat2`), and the golden-output file `sources/test-tools/xfstests/tests/generic/700.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch`, `_require_attrs`, `_require_renameat2 whiteout`, `_fixed_by_fs_commit xfs 70b589a37e1a "xfs: add selinux labels to whiteout inodes"`, `_notrun "Require selinux to be enabled"`.

## Risks and Edge Cases

- Directory mutation and rename races depend on dentry-cache timing and may need repeated attempts to expose regressions.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 700; Silence is golden'. Runtime pass/fail is primarily the command exit status plus golden-output comparison. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
