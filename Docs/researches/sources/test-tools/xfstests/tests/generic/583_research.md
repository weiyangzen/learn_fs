# sources/test-tools/xfstests/tests/generic/583

## Purpose

FS QA Test No. generic/583 Verify ciphertext for v2 encryption policies that use AES-128-CBC-ESSIV to encrypt file contents and AES-128-CTS-CBC to encrypt file names. This is the same as generic/549, except using v2 policies.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick encrypt`. It imports `./common/preamble`, `./common/filter`, `./common/encrypt`. Prerequisite and skip gates include feature gates are delegated to sourced helpers or nested helper routines. No major local helper functions are defined; the scenario is driven directly by the top-level shell flow. External command surfaces and helper binaries visible in the source include standard shell utilities plus xfstests helper functions. Important harness variables and paths include the standard xfstests environment variables.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_verify_ciphertext_for_encryption_policy AES-128-CBC-ESSIV AES-128-CTS-CBC v2`.

## State and Persistence Behavior

The test creates encrypted directories/files and manipulates fscrypt keys or nonce/ciphertext metadata. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

fscrypt policy/key support and raw metadata inspection differ across filesystems and kernel versions. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/583.out`. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
