# sources/test-tools/xfstests/tests/generic/740

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/740`. cross check mkfs detection of foreign filesystems It is registered with `_begin_fstest mkfs auto quick`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 96 source line(s).
- Harness registration: `_begin_fstest mkfs auto quick`.
- Imported common libraries: `./common/preamble`, `./common/filter`.
- Capability and skip gates: `_exclude_fs ext2`, `_exclude_fs ext3`, `_exclude_fs ext4`, `_exclude_fs jfs`, `_exclude_fs ocfs2`, `_exclude_fs udf`, `_require_scratch_nocheck`, `_require_no_large_scratch_dev`, `_require_block_device "${SCRATCH_DEV}"`, `_require_non_zoned_device "${SCRATCH_DEV}"`.
- Local shell functions: none visible.
- External `$here/src` helpers: `$here/src/devzero -n 20 $SCRATCH_DEV >/dev/null`.
- Notable variables and constants:
- `preop="" # for special input needs (usually a prompt)`
- `preargs="" # for any special pre-device options`
- `postargs="" # for any special post-device options`
- `preargs="-F"`
- `preargs=/proc/fs`
- `preop="echo y |"`
- `preargs="-p lock_nolock -j 1"`
- `preop="echo Y |"`
- `postargs=2000`
- `postargs="--quick"`
- `preop="echo y |"`
- `preargs="-f"`

## Control Flow

- Capability gating runs first through `_exclude_fs ext2`, `_exclude_fs ext3`, `_exclude_fs ext4`, `_exclude_fs jfs`, `_exclude_fs ocfs2`, plus 5 more.
- User-visible phase markers include:
- `line 31: echo "Silence is golden."`
- `line 78: echo "=== Creating $fs filesystem..." >>$seqres.full`
- `line 79: echo " ( $preop mkfs -t $fs $preargs $SCRATCH_DEV $postargs )" >>$seqres.full`
- `line 85: echo "=== Attempting $FSTYP overwrite of $fs..." >>$seqres.full`
- `line 90: echo "mkfs of type ${fs} failed" >>$seqres.full`
- Key operational lines include:
- `line 24: _require_scratch_nocheck`
- `line 25: _require_no_large_scratch_dev`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest mkfs auto quick`, common helper libraries (`./common/preamble`, `./common/filter`), and the golden-output file `sources/test-tools/xfstests/tests/generic/740.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_exclude_fs ext2`, `_exclude_fs ext3`, `_exclude_fs ext4`, `_exclude_fs jfs`, `_exclude_fs ocfs2`, `_exclude_fs udf`, `_require_scratch_nocheck`, `_require_no_large_scratch_dev`, plus 2 more.

## Risks and Edge Cases

- Most failures should surface as unexpected output, nonzero helper status, or harness `_fail`/`_notrun` behavior.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 740; Silence is golden.'. Runtime pass/fail is primarily the command exit status plus golden-output comparison. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
