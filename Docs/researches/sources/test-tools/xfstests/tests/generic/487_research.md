# sources/test-tools/xfstests/tests/generic/487

## Purpose

Open a file several times, write to it, fsync on all fds and make sure that they all return 0. Change the device to start throwing errors. Write again on all fds and fsync on all fds. Ensure that we get errors on all of them. Then fsync on all one last time and verify that all return 0.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick eio`. It imports `./common/preamble`, `./common/filter`, `./common/dmerror`. Prerequisite and skip gates include `_require_scratch_nocheck`, `_require_logdev`, `_require_dm_target error`, `_require_fs_space $SCRATCH_MNT $datalen`. Local helper functions: `_cleanup`. External command surfaces and helper binaries visible in the source include `xfs_io`, `mount`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `tmp`, `seq`, `FSTYP`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch_nocheck`; `btrfs)`; `_notrun "btrfs has a specialized test for this"`; `*)`; `_require_logdev`; `_require_dm_target error`; `unset SCRATCH_RTDEV`; `echo "Format and mount"`; `_scratch_mkfs > $seqres.full 2>&1`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; injects block-device, power-fail, shutdown, or thin-provisioning behavior to validate recovery paths; uses explicit sync/fsync/remount points to force persistence boundaries. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

writeback error reporting can be missed, over-reported, or cleared at the wrong time. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/487.out`. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
