# sources/test-tools/xfstests/tests/generic/557

## Purpose

Test that if we fsync a file, evict its inode, unlink it and then fsync its parent directory, after a power failure the file does not exists.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick log`. It imports `./common/preamble`, `./common/filter`, `./common/dmflakey`. Prerequisite and skip gates include `_require_scratch`, `_require_dm_target flakey`, `_require_metadata_journaling $SCRATCH_DEV`. Local helper functions: `_cleanup`. External command surfaces and helper binaries visible in the source include `xfs_io`, `mkdir`, `touch`, `sleep`, `kill`, `wait`. Important harness variables and paths include `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres.full`, `tmp`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch`; `_require_dm_target flakey`; `_scratch_mkfs >>$seqres.full 2>&1`; `_require_metadata_journaling $SCRATCH_DEV`; `_init_flakey`; `_scratch_mount`; `mkdir $SCRATCH_MNT/dir`; `touch $SCRATCH_MNT/dir/foo`; `$XFS_IO_PROG -c "fsync" $SCRATCH_MNT/dir/foo`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; injects block-device, power-fail, shutdown, or thin-provisioning behavior to validate recovery paths; uses explicit sync/fsync/remount points to force persistence boundaries. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

ordering bugs in journal replay or fsync logging can lose metadata or data after simulated power loss. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/557.out`; success is mostly silence after prerequisite and operation checks. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
