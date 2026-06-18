# sources/test-tools/xfstests/tests/generic/572

## Purpose

FS QA Test generic/572 This is a basic fs-verity test which verifies: - conditions for enabling verity - verity files have correct contents and size - can't change contents of verity files, but can change metadata - can retrieve a verity file's digest via FS_IOC_MEASURE_VERITY

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick verity`. It imports `./common/preamble`, `./common/filter`, `./common/verity`. Prerequisite and skip gates include `_require_scratch_verity`. Local helper functions: `_cleanup`, `filter_output`, `verify_data_readable`. External command surfaces and helper binaries visible in the source include `fsverity`, `xfs_io`, `mkdir`, `perl`, `sleep`, `kill`, `wait`, `mv`, `ln`, `chmod`, `chown`, `cp`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `tmp`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch_verity`; `_disable_fsverity_signatures`; `_scratch_mkfs_verity &>> $seqres.full`; `_scratch_mount`; `_fsv_scratch_begin_subtest "Enabling verity on file with verity already enabled fails with EEXIST"`; `_fsv_create_enable_file $fsv_file`; `echo "(trying again)"`; `_fsv_enable $fsv_file |& filter_output`; `_fsv_scratch_begin_subtest "Enabling verity with invalid hash algorithm fails with EINVAL"`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

environmental skips and helper availability can dominate failures, so `_require_*` gates are part of the contract. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/572.out`; content dumps/hexdumps expose corruption or unexpected nonzero data. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
