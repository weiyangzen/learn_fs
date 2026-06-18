# sources/test-tools/xfstests/tests/generic/535

## Purpose

This testcase is trying to test recovery flow of generic filesystem, w/ below steps, once i_mode changes, after we fsync that file, we can expect that i_mode can be recovered after sudden power-cuts. 1. touch testfile or mkdir testdir 2. chmod 777 testfile/testdir 3. sync 4. chmod 755 testfile/testdir 5. fsync testfile/testdir 6. record last i_mode 7. flakey drop 8. remount 9. check i_mode

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick log`. It imports `./common/preamble`, `./common/filter`, `./common/dmflakey`. Prerequisite and skip gates include `_require_scratch`, `_require_dm_target flakey`, `_require_metadata_journaling $SCRATCH_DEV`. Local helper functions: `_cleanup`, `do_check`. External command surfaces and helper binaries visible in the source include `xfs_io`, `touch`, `mkdir`, `chmod`, `stat`. Important harness variables and paths include `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres.full`, `tmp`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch`; `_require_dm_target flakey`; `_scratch_mkfs >/dev/null 2>&1`; `_require_metadata_journaling $SCRATCH_DEV`; `_init_flakey`; `echo "Silence is golden"`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; injects block-device, power-fail, shutdown, or thin-provisioning behavior to validate recovery paths; uses explicit sync/fsync/remount points to force persistence boundaries. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

ordering bugs in journal replay or fsync logging can lose metadata or data after simulated power loss. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/535.out`; success is mostly silence after prerequisite and operation checks; content dumps/hexdumps expose corruption or unexpected nonzero data. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
