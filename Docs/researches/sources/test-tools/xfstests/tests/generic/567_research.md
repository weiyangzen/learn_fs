# sources/test-tools/xfstests/tests/generic/567

## Purpose

FS QA Test No. generic/567 Test mapped writes against punch-hole to ensure we get the data correctly written. This can expose data corruption bugs on filesystems where the block size is smaller than the page size. (generic/029 is a similar test but for truncate.)

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick rw punch mmap`. It imports `./common/preamble`, `./common/filter`. Prerequisite and skip gates include `_require_scratch`, `_require_xfs_io_command "fpunch"`. No major local helper functions are defined; the scenario is driven directly by the top-level shell flow. External command surfaces and helper binaries visible in the source include `xfs_io`, `truncate`. Important harness variables and paths include `SCRATCH_MNT`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch`; `_require_xfs_io_command "fpunch"`; `_scratch_mkfs > /dev/null 2>&1`; `_scratch_mount`; `$XFS_IO_PROG -t -f -c "pwrite -S 0x58 0 12288" -c "mmap -rw 0 12288" -c "mwrite -S 0x5a 2048 8192" -c "fpunch 2048 8192" -c "mwrite -S 0x...`; `echo "==== Pre-Remount ==="`; `_hexdump $testfile`; `_scratch_cycle_mount`; `echo "==== Post-Remount =="`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

I/O path races may be timing-sensitive and surface only under mmap, direct I/O, io_uring, or fsx replay stress. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/567.out`; content dumps/hexdumps expose corruption or unexpected nonzero data. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
