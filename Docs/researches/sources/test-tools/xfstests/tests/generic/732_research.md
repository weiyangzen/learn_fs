# sources/test-tools/xfstests/tests/generic/732

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/732`. Mount the same export to different mount points and move (rename) files among those mount points. This simple test recently unveils an ancient nfsd bug that is fixed by fdd2630a739819 ("nfsd: fix change_info in NFSv4 RENAME replies"). It is registered with `_begin_fstest auto quick rename`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 55 source line(s).
- Harness registration: `_begin_fstest auto quick rename`.
- Imported common libraries: `./common/preamble`.
- Capability and skip gates: `_exclude_fs nfs`, `_exclude_fs overlay`, `_exclude_fs tmpfs`, `_require_test`, `_require_scratch`.
- Local shell functions: `_cleanup`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `testdir1=$TEST_DIR/mountpoint1-$seq`
- `testdir2=$TEST_DIR/mountpoint2-$seq`
- `SCRATCH_MNT=$testdir1 _scratch_mount`
- `SCRATCH_MNT=$testdir2 _scratch_mount`

## Control Flow

- Capability gating runs first through `_exclude_fs nfs`, `_exclude_fs overlay`, `_exclude_fs tmpfs`, `_require_test`, `_require_scratch`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- User-visible phase markers include:
- `line 34: echo "Silence is golden"`
- Key operational lines include:
- `line 18: _unmount $testdir1 2>/dev/null`
- `line 19: _unmount $testdir2 2>/dev/null`
- `line 36: _scratch_mkfs >> $seqres.full`
- `line 42: SCRATCH_MNT=$testdir1 _scratch_mount`
- `line 43: SCRATCH_MNT=$testdir2 _scratch_mount`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick rename`, common helper libraries (`./common/preamble`), and the golden-output file `sources/test-tools/xfstests/tests/generic/732.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_exclude_fs nfs`, `_exclude_fs overlay`, `_exclude_fs tmpfs`, `_require_test`, `_require_scratch`.

## Risks and Edge Cases

- Feature gates depend on kernel, userspace tool, and filesystem support; unsupported features correctly produce `_notrun`.
- Directory mutation and rename races depend on dentry-cache timing and may need repeated attempts to expose regressions.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 732; Silence is golden'. Runtime pass/fail is primarily the command exit status plus golden-output comparison. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
