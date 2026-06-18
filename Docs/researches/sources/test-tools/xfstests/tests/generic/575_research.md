# sources/test-tools/xfstests/tests/generic/575

## Purpose

FS QA Test generic/575 Test that fs-verity is using the correct file digest values. This test verifies that fs-verity is doing its Merkle tree-based hashing correctly, i.e. that it hasn't been broken by a change.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick verity`. It imports `./common/preamble`, `./common/filter`, `./common/verity`. Prerequisite and skip gates include `_require_scratch_verity`. Local helper functions: `_cleanup`, `test_alg_with_block_size`. External command surfaces and helper binaries visible in the source include `cp`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `tmp`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch_verity`; `_disable_fsverity_signatures`; `_scratch_mkfs_verity &>> $seqres.full`; `_scratch_mount`; `algs=(sha256 sha512)`; `block_sizes=(1024 4096)`; `salts=('' '' '' '--salt=' '--salt=f3c93fa6fb828c0e1587e5714ecf6f56')`; `sha256:f2cca36b9b1b7f07814e4284b10121809133e7cb9c4528c8f6846e85fc624ffa`; `sha256:ea08590a4fe9c3d6c9dafe0eedacd9dffff8f24e24f1865ee3af132a495ab087`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

environmental skips and helper availability can dominate failures, so `_require_*` gates are part of the contract. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/575.out`. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
