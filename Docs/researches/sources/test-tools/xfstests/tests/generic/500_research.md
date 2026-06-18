# sources/test-tools/xfstests/tests/generic/500

## Purpose

Race test running out of data space with concurrent discard operation on dm-thin. If a user constructs a test that loops repeatedly over below steps on dm-thin, block allocation can fail due to discards not having completed yet (Fixed by a685557 dm thin: handle running out of data space vs concurrent discard): 1) fill thin device via filesystem file 2) remove file 3) fstrim And this maybe cause a deadlock when racing a fstrim with a filesystem (XFS) shutdown. (Fixed by 8c81dd46ef3c Force log to disk before reading the AGF during a fstrim)

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto thin trim`. It imports `./common/preamble`, `./common/filter`, `./common/dmthin`. Prerequisite and skip gates include `_require_scratch_nocheck`, `_require_dm_target thin-pool`, `_exclude_fs btrfs`, `_require_batched_discard $SCRATCH_MNT`. Local helper functions: `_cleanup`. External command surfaces and helper binaries visible in the source include `xfs_io`, `fstrim`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `tmp`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch_nocheck`; `_require_dm_target thin-pool`; `_exclude_fs btrfs`; `_scratch_mkfs >>$seqres.full 2>&1`; `_scratch_mount`; `_require_batched_discard $SCRATCH_MNT`; `_scratch_unmount`; `BACKING_SIZE=$((128 * 1024 * 1024 / 512))	# 128M`; `VIRTUAL_SIZE=$((BACKING_SIZE + 1024))		# 128M + 1k`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; injects block-device, power-fail, shutdown, or thin-provisioning behavior to validate recovery paths. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

dm-thin exhaustion/discard races can hang or fail depending on kernel/device-mapper fixes. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/500.out`; success is mostly silence after prerequisite and operation checks. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
