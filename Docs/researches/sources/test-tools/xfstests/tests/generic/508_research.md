# sources/test-tools/xfstests/tests/generic/508

## Purpose

This testcase is trying to test recovery flow of generic filesystem, it needs creation time support on specified filesystem. With below steps, once the file is created, creation time attribute should be valid on the file, after we fsync that file, it expects creation time can be recovered after sudden power-cuts. 1. touch testfile; 1.1 sync (optional) 2. xfs_io -f testfile -c "fsync"; 3. godown; 4. umount; 5. mount; 6. check creation time

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest shutdown auto quick metadata`. It imports `./common/preamble`, `./common/filter`. Prerequisite and skip gates include `_require_test_lsattr`, `_require_statx`, `_require_xfs_io_command "statx" "-v"`, `_require_scratch`, `_require_scratch_shutdown`, `_require_scratch_btime`, `_require_metadata_journaling $SCRATCH_DEV`. Local helper functions: `do_check`. External command surfaces and helper binaries visible in the source include `xfs_io`, `touch`, `umount`, `mount`, `grep`. Important harness variables and paths include `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres.full`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_test_lsattr`; `_require_statx`; `_require_xfs_io_command "statx" "-v"`; `_require_scratch`; `_require_scratch_shutdown`; `_require_scratch_btime`; `_scratch_mkfs >/dev/null 2>&1`; `_require_metadata_journaling $SCRATCH_DEV`; `echo "Silence is golden"`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; injects block-device, power-fail, shutdown, or thin-provisioning behavior to validate recovery paths; uses explicit sync/fsync/remount points to force persistence boundaries. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

ordering bugs in journal replay or fsync logging can lose metadata or data after simulated power loss. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/508.out`; success is mostly silence after prerequisite and operation checks; grep-based checks assert expected metadata or data is still visible. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
