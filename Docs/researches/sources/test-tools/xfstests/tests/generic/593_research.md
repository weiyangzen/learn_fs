# sources/test-tools/xfstests/tests/generic/593

## Purpose

Test adding a key to a filesystem's fscrypt keyring via an "fscrypt-provisioning" keyring key. This is an alternative to the normal method where the raw key is given directly.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick encrypt`. It imports `./common/preamble`, `./common/filter`, `./common/encrypt`. Prerequisite and skip gates include `_require_scratch_encryption -v 2`, `_require_command "$KEYCTL_PROG" keyctl`, `_require_add_enckey_by_key_id $SCRATCH_MNT`. Local helper functions: `test_with_policy_version`. External command surfaces and helper binaries visible in the source include `keyctl`, `xfs_io`, `mkdir`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch_encryption -v 2`; `_require_command "$KEYCTL_PROG" keyctl`; `_init_session_keyring`; `_scratch_mkfs_encrypted &>> $seqres.full`; `_scratch_mount`; `_require_add_enckey_by_key_id $SCRATCH_MNT`; `test_with_policy_version 1`; `test_with_policy_version 2`; `echo`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; creates encrypted directories/files and manipulates fscrypt keys or nonce/ciphertext metadata. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

fscrypt policy/key support and raw metadata inspection differ across filesystems and kernel versions. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/593.out`; content dumps/hexdumps expose corruption or unexpected nonzero data. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
