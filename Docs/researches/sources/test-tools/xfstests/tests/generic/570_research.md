# sources/test-tools/xfstests/tests/generic/570

## Purpose

Check that we can't modify a block device that's an active swap device.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick rw swap mmap`. It imports `./common/preamble`, `./common/filter`. Prerequisite and skip gates include `_require_test_program swapon`, `_require_scratch_nocheck`, `_require_block_device $SCRATCH_DEV`, `_require_odirect`, `_require_non_zoned_device "$SCRATCH_DEV"`. Local helper functions: `_cleanup`. External command surfaces and helper binaries visible in the source include `mkswap`, `xfs_io`, `swapon`, `swapoff`. Important harness variables and paths include `SCRATCH_DEV`, `seqres.full`, `tmp`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_test_program swapon`; `_require_scratch_nocheck`; `_require_block_device $SCRATCH_DEV`; `_require_odirect`; `_require_non_zoned_device "$SCRATCH_DEV"`; `test -e /dev/snapshot && _notrun "userspace hibernation to swap is enabled"`; `$MKSWAP_PROG "$SCRATCH_DEV" >> $seqres.full`; `echo "verb $verb"`; `"$here/src/swapon" -v $verb $SCRATCH_DEV`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; temporarily activates swap files and must clean them with `swapoff`. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

active swapfiles must reject extent-changing operations and require page-size/block-size compatibility; I/O path races may be timing-sensitive and surface only under mmap, direct I/O, io_uring, or fsx replay stress. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/570.out`. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
