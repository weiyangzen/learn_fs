# sources/test-tools/xfstests/tests/generic/547

## Purpose

Run fsstress, fsync every file and directory, simulate a power failure and then verify that all files and directories exist, with the same data and metadata they had before the power failure.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick log`. It imports `./common/preamble`, `./common/filter`, `./common/dmflakey`. Prerequisite and skip gates include `_require_test`, `_require_scratch`, `_require_fssum`, `_require_dm_target flakey`, `_require_metadata_journaling $SCRATCH_DEV`. Local helper functions: `_cleanup`. External command surfaces and helper binaries visible in the source include `xfs_io`, `fssum`, `fsstress`, `seq`, `mkdir`, `mount`. Important harness variables and paths include `SCRATCH_MNT`, `SCRATCH_DEV`, `TEST_DIR`, `seqres.full`, `tmp`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_test`; `_require_scratch`; `_require_fssum`; `_require_dm_target flakey`; `rm -fr $fssum_files_dir`; `mkdir $fssum_files_dir`; `_scratch_mkfs >>$seqres.full 2>&1`; `_require_metadata_journaling $SCRATCH_DEV`; `_init_flakey`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; uses the configured test filesystem under `TEST_DIR` without necessarily reformatting it; injects block-device, power-fail, shutdown, or thin-provisioning behavior to validate recovery paths; uses explicit sync/fsync/remount points to force persistence boundaries. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

ordering bugs in journal replay or fsync logging can lose metadata or data after simulated power loss. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/547.out`; fssum before/after comparison validates tree integrity. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
