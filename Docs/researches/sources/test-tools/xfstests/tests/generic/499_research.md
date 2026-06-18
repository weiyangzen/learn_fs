# sources/test-tools/xfstests/tests/generic/499

## Purpose

Test a specific sequence of fsx operations that causes an mmap read past eof to return nonzero contents.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick rw collapse zero prealloc mmap`. It imports `./common/preamble`, `./common/punch`. Prerequisite and skip gates include `_require_scratch`, `_require_xfs_io_command "falloc" "-k"`, `_require_xfs_io_command "fcollapse"`, `_require_xfs_io_command "fzero"`. No major local helper functions are defined; the scenario is driven directly by the top-level shell flow. External command surfaces and helper binaries visible in the source include `fsx`, `truncate`, `touch`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `tmp`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch`; `_require_xfs_io_command "falloc" "-k"`; `_require_xfs_io_command "fcollapse"`; `_require_xfs_io_command "fzero"`; `_scratch_mkfs >>$seqres.full 2>&1`; `_scratch_mount`; `writes a deterministic fsx replay script`; `fallocate 0x77e2 0x5f06 0x269a2 keep_size`; `mapwrite 0x2e7fc 0x42ba 0x3f989`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

I/O path races may be timing-sensitive and surface only under mmap, direct I/O, io_uring, or fsx replay stress. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/499.out`; success is mostly silence after prerequisite and operation checks; fsx/fsstress style stress exits cleanly and emits only filtered diagnostics. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
