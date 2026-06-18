# sources/test-tools/xfstests/tests/generic/590

## Purpose

Tests writing into big fallocates. Based on an XFS RT subvolume specific test now split into xfs/650.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto prealloc preallocrw`. It imports `./common/preamble`, `./common/filter`. Prerequisite and skip gates include `_require_xfs_io_command "falloc"`, `_require_fs_space "$SCRATCH_MNT" $((filesz / 1024))`. No major local helper functions are defined; the scenario is driven directly by the top-level shell flow. External command surfaces and helper binaries visible in the source include `xfs_io`, `truncate`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_xfs_io_command "falloc"`; `maxextlen=$((0x1fffff))`; `_scratch_mkfs >>$seqres.full 2>&1`; `_scratch_mount`; `_require_fs_space "$SCRATCH_MNT" $((filesz / 1024))`; `$XFS_IO_PROG -c "falloc 0 $filesz" -c fsync -f "$SCRATCH_MNT/file"`; `$XFS_IO_PROG -c "pwrite -b 1M -W 0 $(((maxextlen + 2 - rextsize) * bs))" "$SCRATCH_MNT/file" >> "$seqres.full"`; `$XFS_IO_PROG -c "truncate 0" -c fsync "$SCRATCH_MNT/file"`; `_scratch_unmount`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; uses explicit sync/fsync/remount points to force persistence boundaries. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

I/O path races may be timing-sensitive and surface only under mmap, direct I/O, io_uring, or fsx replay stress. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/590.out`; success is mostly silence after prerequisite and operation checks. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
