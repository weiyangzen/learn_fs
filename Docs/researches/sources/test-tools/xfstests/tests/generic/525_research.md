# sources/test-tools/xfstests/tests/generic/525

## Purpose

All Rights Reserved. Check that high-offset reads and writes work. This is a variant of test generic/466 for filesystems that do not support mkfs_sized.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick rw`. It imports `./common/preamble`, `./common/filter`. Prerequisite and skip gates include `_require_scratch`. No major local helper functions are defined; the scenario is driven directly by the top-level shell flow. External command surfaces and helper binaries visible in the source include `bc`, `xfs_io`, `truncate`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch`; `_scratch_mkfs >>$seqres.full 2>&1`; `_scratch_mount`; `echo "++ Create the original files" >> $seqres.full`; `bigoff=$(echo "2^63 - 2" | $BC_PROG)`; `len=$(echo "2^63 - 1" | $BC_PROG)`; `$XFS_IO_PROG -f -c "truncate $len" $testdir/file0 >> $seqres.full 2>&1`; `_notrun "filesystem does not support huge file size"`; `_pwrite_byte 0x61 $bigoff 1 $testdir/file1 >> $seqres.full`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

I/O path races may be timing-sensitive and surface only under mmap, direct I/O, io_uring, or fsx replay stress. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/525.out`. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
