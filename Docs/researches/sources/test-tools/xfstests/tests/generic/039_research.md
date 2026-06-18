# sources/test-tools/xfstests/tests/generic/039

## Purpose

This test is motivated by an fsync issue discovered in btrfs. The issue was that after fsyncing an inode that got its link count decremented, and the new link count is greater than zero, after the fsync log replay the inode's parent directory metadata became inconsistent - it had a wrong i_size and dangling index entries which prevented the directory from ever being removed (rmdir always failed with -ENOTEMPTY, even if the directory had no more child inodes). The btrfs issue was fixed by the following linux kernel.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest metadata auto quick log`. Important local functions are `_cleanup`. Key xfstests/helper interfaces include `_require_dm_target` (requires a device-mapper target), `_require_scratch` (requires a disposable scratch filesystem), `_scratch_mount` (mounts the scratch filesystem), `_scratch_mkfs` (formats the scratch filesystem). External or helper commands visible in the body include `ln`, `mkdir`, `rm`. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, `./common/dmflakey`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_cleanup()`; `_cleanup_flakey`; `_require_scratch`; `_require_hardlinks`; `_require_dm_target flakey`; `_scratch_mkfs >> $seqres.full 2>&1`; `_require_metadata_journaling $SCRATCH_DEV`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state, device-mapper target state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_dm_target`, `_require_hardlinks`, `_require_metadata_journaling`, `_require_scratch`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter`, `./common/dmflakey` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: prints `Silence is golden` after all checks pass; logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.
