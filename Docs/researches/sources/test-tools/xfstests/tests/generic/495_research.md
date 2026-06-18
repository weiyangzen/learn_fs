# sources/test-tools/xfstests/tests/generic/495

## Purpose

Test invalid swap file (with holes)

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick swap`. It imports `./common/preamble`, `./common/filter`. Prerequisite and skip gates include `_require_scratch_swapfile`, `_require_test_program mkswap`, `_require_test_program swapon`, `_require_sparse_files`. No major local helper functions are defined; the scenario is driven directly by the top-level shell flow. External command surfaces and helper binaries visible in the source include `chattr`, `xfs_io`, `mkswap`, `swapon`, `touch`, `chmod`, `truncate`, `swapoff`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch_swapfile`; `_require_test_program mkswap`; `_require_test_program swapon`; `_require_sparse_files`; `_scratch_mkfs >> $seqres.full 2>&1`; `_scratch_mount`; `blksize=$(_get_file_block_size $SCRATCH_MNT)`; `test $blksize -eq $(getconf PAGE_SIZE) || _notrun "swap file allocation unit size must match page size"`; `touch "$SCRATCH_MNT/swap"`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; temporarily activates swap files and must clean them with `swapoff`. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

active swapfiles must reject extent-changing operations and require page-size/block-size compatibility. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/495.out`; content dumps/hexdumps expose corruption or unexpected nonzero data. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
