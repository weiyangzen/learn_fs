# sources/test-tools/xfstests/tests/generic/690

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/690`. Test that if we fsync a directory, create a symlink inside it, rename the symlink, fsync again the directory and then power fail, after the filesystem is mounted again, the symlink exists with the new name and it has the correct content. On btrfs this used to result in the symlink being empty (i_size 0), and it was fixed by kernel commit: d0e64a981fd841 ("btrfs: always log symlinks in full mode") It is registered with `_begin_fstest auto quick log`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 87 source line(s).
- Harness registration: `_begin_fstest auto quick log`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/dmflakey`.
- Capability and skip gates: `_require_scratch`, `_require_symlinks`, `_require_dm_target flakey`, `_require_metadata_journaling $SCRATCH_DEV`.
- Local shell functions: `_cleanup`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `symlink_content=$(readlink "$SCRATCH_MNT"/testdir/baz | _filter_scratch)`

## Control Flow

- Capability gating runs first through `_require_scratch`, `_require_symlinks`, `_require_dm_target flakey`, `_require_metadata_journaling $SCRATCH_DEV`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- User-visible phase markers include:
- `line 59: echo -n > "$SCRATCH_MNT"/testdir/foo`
- `line 81: echo "symlink content: ${symlink_content}"`
- Key operational lines include:
- `line 22: _cleanup_flakey`
- `line 46: _scratch_mkfs >>$seqres.full 2>&1`
- `line 48: _init_flakey`
- `line 49: _scratch_mount`
- `line 55: _scratch_sync`
- `line 62: $XFS_IO_PROG -c "fsync" "$SCRATCH_MNT"/testdir`
- `line 71: $XFS_IO_PROG -c "fsync" "$SCRATCH_MNT"/testdir`
- `line 75: _flakey_drop_and_remount`
- `line 83: _scratch_unmount`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Synthetic block-device state can be introduced through device-mapper, loop, SCSI debug, or huge-device helpers and must be cleaned even on failure. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick log`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/dmflakey`), and the golden-output file `sources/test-tools/xfstests/tests/generic/690.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch`, `_require_symlinks`, `_require_dm_target flakey`, `_require_metadata_journaling $SCRATCH_DEV`.

## Risks and Edge Cases

- Failure-injection paths can leave mounts or synthetic device tables behind if cleanup is interrupted.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 690; symlink content: SCRATCH_MNT/testdir/foo'. Runtime pass/fail is also signaled by post-remount or failure-injection persistence checks. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
