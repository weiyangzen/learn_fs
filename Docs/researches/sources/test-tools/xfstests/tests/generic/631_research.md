# sources/test-tools/xfstests/tests/generic/631

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/631`. Reproducer for a deadlock in xfs_rename reported by Wenli Xie. When overlayfs is running on top of xfs and the user unlinks a file in the overlay, overlayfs will create a whiteout inode and ask us to "rename" the whiteout file atop the one being unlinked. If the file being unlinked loses its one nlink, we then have to put the inode on the unlinked list. This requires us to grab the AGI buffer of the whiteout inode to take it off the unlinked list (which is where whiteouts are created) and to grab the AGI buffer of the file being deleted. If the whiteout was created in a higher numbered AG than the file being deleted, we'll lock the AGIs in the wrong order and deadlock. Note that this test doesn't do anything... It is registered with `_begin_fstest auto rw whiteout rename`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 103 source line(s).
- Harness registration: `_begin_fstest auto rw whiteout rename`.
- Imported common libraries: `./common/preamble`, `./common/attr`.
- Capability and skip gates: `_require_scratch`, `_require_attrs trusted`, `_exclude_fs overlay`, `_require_extra_fs overlay`, `_fixed_by_fs_commit xfs 6da1b4b1ab36 "xfs: fix an ABBA deadlock in xfs_rename"`.
- Local shell functions: `_cleanup`, `stop_workers`, `worker`.
- External `$here/src` helpers: none visible.

## Control Flow

- Capability gating runs first through `_require_scratch`, `_require_attrs trusted`, `_exclude_fs overlay`, `_require_extra_fs overlay`, `_fixed_by_fs_commit xfs 6da1b4b1ab36 "xfs: fix an ABBA deadlock in xfs_rename"`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- User-visible phase markers include:
- `line 54: echo salts > $SCRATCH_MNT/lowerdir/etc/access.conf`
- `line 100: echo Silence is golden.`
- Key operational lines include:
- `line 46: _scratch_mkfs >> $seqres.full`
- `line 47: _scratch_mount`
- `line 61: while [ "$(ls $SCRATCH_MNT/workers/ | wc -l)" -gt 0 ]; do`
- `line 88: _unmount $mergedir`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Extended attributes are part of the persistent state being created, replayed, or verified. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto rw whiteout rename`, common helper libraries (`./common/preamble`, `./common/attr`), and the golden-output file `sources/test-tools/xfstests/tests/generic/631.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch`, `_require_attrs trusted`, `_exclude_fs overlay`, `_require_extra_fs overlay`, `_fixed_by_fs_commit xfs 6da1b4b1ab36 "xfs: fix an ABBA deadlock in xfs_rename"`.

## Risks and Edge Cases

- Feature gates depend on kernel, userspace tool, and filesystem support; unsupported features correctly produce `_notrun`.
- Directory mutation and rename races depend on dentry-cache timing and may need repeated attempts to expose regressions.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 631; Silence is golden.'. Runtime pass/fail is also signaled by hang/race detection through background work, loops, or timeout windows. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
