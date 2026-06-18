# sources/test-tools/xfstests/tests/generic/518

## Purpose

Test that we can not clone a range from a file A into the middle of a file B when the range includes the last block of file A and file A's size is not aligned with the filesystem's block size. Allowing such case would lead to data corruption since the data between EOF and the end of its block is undefined.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick clone`. It imports `./common/preamble`, `./common/filter`, `./common/reflink`. Prerequisite and skip gates include `_require_scratch_reflink`. No major local helper functions are defined; the scenario is driven directly by the top-level shell flow. External command surfaces and helper binaries visible in the source include `xfs_io`, `mount`, `od`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch_reflink`; `_scratch_mkfs >>$seqres.full 2>&1`; `_scratch_mount`; `foo_size=$((256 * 1024 + 100)) # 256Kb + 100 bytes`; `$XFS_IO_PROG -f -c "pwrite -S 0x3c 0 $foo_size" $SCRATCH_MNT/foo | _filter_xfs_io`; `$XFS_IO_PROG -f -c "pwrite -S 0xb5 0 $bar_size" $SCRATCH_MNT/bar | _filter_xfs_io`; `$XFS_IO_PROG -c "reflink $SCRATCH_MNT/foo 0 512K $foo_size" $SCRATCH_MNT/bar`; `_scratch_cycle_mount`; `echo "File content after failed reflink:"`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

shared extent, COW, or dedupe paths can corrupt unrelated file ranges or violate swapfile restrictions. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/518.out`; content dumps/hexdumps expose corruption or unexpected nonzero data. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
