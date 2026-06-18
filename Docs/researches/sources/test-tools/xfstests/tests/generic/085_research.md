# sources/test-tools/xfstests/tests/generic/085

## Purpose

Exercise fs freeze/unfreeze and mount/umount race, which could lead to use-after-free oops. This commit fixed the issue: 1494583 fix get_active_super()/umount() race

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest auto freeze mount`. Important local functions are `_cleanup`, `cleanup_dmdev`, `setup_dmdev`. Key xfstests/helper interfaces include `_scratch_mkfs_sized` (formats a scratch image/device of a requested size), `_require_dm_target` (requires a device-mapper target), `_require_scratch` (requires a disposable scratch filesystem). External or helper commands visible in the body include `mount`, `rm`. Significant variables include `size`, `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_cleanup()`; `rm -f $tmp.*`; `if [ -n "$pid" ]; then`; `_unmount -q $SCRATCH_MNT >/dev/null 2>&1`; `_dmsetup_remove $node`; `_require_scratch`; `_require_block_device $SCRATCH_DEV`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state, device-mapper target state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_block_device`, `_require_dm_target`, `_require_freeze`, `_require_scratch`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: prints `Silence is golden` after all checks pass; logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.
