# sources/test-tools/xfstests/tests/generic/507

## Purpose

This testcase is trying to test recovery flow of generic filesystem, w/ below steps, once i_flags changes, after we fsync that file, we can expect that i_flags can be recovered after sudden power-cuts. 1. touch testfile; 1.1 sync (optional) 2. chattr +[ASai] testfile 3. xfs_io -f testfile -c "fsync"; 4. godown; 5. umount; 6. mount; 7. check i_flags 8. chattr -[ASai] testfile 9. xfs_io -f testfile -c "fsync"; 10. godown; 11. umount; 12. mount; 13. check i_flags

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest shutdown auto quick metadata`. It imports `./common/preamble`, `./common/filter`. Prerequisite and skip gates include `_require_command "$LSATTR_PROG" lasttr`, `_require_command "$CHATTR_PROG" chattr`, `_require_chattr ASai`, `_require_scratch`, `_require_scratch_shutdown`, `_require_metadata_journaling $SCRATCH_DEV`. Local helper functions: `_cleanup`, `do_check`. External command surfaces and helper binaries visible in the source include `chattr`, `lsattr`, `xfs_io`, `touch`, `umount`, `mount`. Important harness variables and paths include `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres.full`, `tmp`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_command "$LSATTR_PROG" lasttr`; `_require_command "$CHATTR_PROG" chattr`; `_require_chattr ASai`; `_require_scratch`; `_require_scratch_shutdown`; `_scratch_mkfs >/dev/null 2>&1`; `_require_metadata_journaling $SCRATCH_DEV`; `echo "Silence is golden"`; `opts="A S a i"`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; injects block-device, power-fail, shutdown, or thin-provisioning behavior to validate recovery paths; uses explicit sync/fsync/remount points to force persistence boundaries. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

ordering bugs in journal replay or fsync logging can lose metadata or data after simulated power loss. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/507.out`; success is mostly silence after prerequisite and operation checks. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
