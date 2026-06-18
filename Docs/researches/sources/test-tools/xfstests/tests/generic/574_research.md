# sources/test-tools/xfstests/tests/generic/574

## Purpose

FS QA Test generic/574 Test corrupting verity files. This test corrupts various parts of the contents of a verity file, or parts of its Merkle tree, by writing directly to the block device. It verifies that this causes I/O errors when the relevant part of the contents is later read by any means.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick verity mmap`. It imports `./common/preamble`, `./common/filter`, `./common/verity`. Prerequisite and skip gates include `_require_scratch_verity`, `_require_fsverity_corruption`. Local helper functions: `_cleanup`, `setup_zeroed_file`, `corruption_test`, `corrupt_eof_block_test`, `test_block_size`. External command surfaces and helper binaries visible in the source include `cp`, `grep`, `mount`, `seq`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `tmp`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch_verity`; `_disable_fsverity_signatures`; `_require_fsverity_corruption`; `_scratch_mkfs_verity &>> $seqres.full`; `_scratch_mount`; `_fsv_scratch_begin_subtest "Testing block_size=FSV_BLOCK_SIZE"`; `test_block_size $FSV_BLOCK_SIZE`; `_fsv_scratch_begin_subtest "Testing block_size=$block_size if supported"`; `continue # Skip redundant test case.`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

I/O path races may be timing-sensitive and surface only under mmap, direct I/O, io_uring, or fsx replay stress. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/574.out`; grep-based checks assert expected metadata or data is still visible. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
