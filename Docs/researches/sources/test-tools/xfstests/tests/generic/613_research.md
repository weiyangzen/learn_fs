# sources/test-tools/xfstests/tests/generic/613

## Purpose

Test that encryption nonces are unique and random, where randomness is approximated as "incompressible by the xz program". An encryption nonce is the 16-byte value that the filesystem generates for each encrypted file. These nonces must be unique in order to cause different files to be encrypted differently, which is an important security property. In practice, they need to be random to achieve that; and it's easy enough to test for both uniqueness and randomness, so we test for both.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick encrypt`. It imports `./common/preamble`, `./common/filter`, `./common/encrypt`. Prerequisite and skip gates include `_require_scratch_encryption -v 2`, `_require_get_encryption_nonce_support`, `_require_command "$XZ_PROG" xz`. No major local helper functions are defined; the scenario is driven directly by the top-level shell flow. External command surfaces and helper binaries visible in the source include `xz`, `mkdir`, `stat`, `touch`, `sort`, `uniq`. Important harness variables and paths include `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres.full`, `tmp`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch_encryption -v 2`; `_require_get_encryption_nonce_support`; `_require_command "$XZ_PROG" xz`; `_scratch_mkfs_encrypted &>> $seqres.full`; `_scratch_mount`; `echo -e "\n# Adding encryption keys"`; `_add_enckey $SCRATCH_MNT "$TEST_RAW_KEY"`; `_add_enckey $SCRATCH_MNT "$TEST_RAW_KEY" -d $TEST_KEY_DESCRIPTOR`; `echo -e "\n# Creating encrypted files and directories"`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; creates encrypted directories/files and manipulates fscrypt keys or nonce/ciphertext metadata. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

fscrypt policy/key support and raw metadata inspection differ across filesystems and kernel versions. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/613.out`. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
