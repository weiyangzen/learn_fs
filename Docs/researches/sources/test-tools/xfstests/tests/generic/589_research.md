# sources/test-tools/xfstests/tests/generic/589

## Purpose

Test mount shared subtrees, verify the move semantics: --------------------------------------------------------------------------- | MOVE MOUNT OPERATION | |************************************************************************** |source(A)->| shared | private | slave | unbindable | | dest(B) | | | | | | | | | | | | | v | | | | | |************************************************************************** | shared | shared | shared | shared & slave | invalid | | | | | | | |non-shared| shared | private | slave | unbindable | *************************************************************************** NOTE: moving a mount residing under a shared mount is invalid. -----------------------------------------------------------------------

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto mount`. It imports `./common/preamble`, `./common/filter`. Prerequisite and skip gates include `_require_test`, `_require_scratch`, `_require_local_device $SCRATCH_DEV`. Local helper functions: `_cleanup`, `fs_stress`, `find_mnt`, `start_test`, `end_test`, `move_run`, `move_test`. External command surfaces and helper binaries visible in the source include `mount`, `seq`, `mkdir`, `sort`. Important harness variables and paths include `SCRATCH_DEV`, `TEST_DIR`, `seqres.full`, `tmp`, `seq`, `FSTYP`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_test`; `_require_scratch`; `_require_local_device $SCRATCH_DEV`; `rm -rf $SRCHEAD $DSTHEAD`; `mkdir $SRCHEAD $DSTHEAD 2>>$seqres.full`; `_mount --make-shared $TEST_DIR`; `move_test`; `_mount --make-private $TEST_DIR`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; uses the configured test filesystem under `TEST_DIR` without necessarily reformatting it; uses explicit sync/fsync/remount points to force persistence boundaries. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

environmental skips and helper availability can dominate failures, so `_require_*` gates are part of the contract. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/589.out`. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
