# sources/test-tools/xfstests/tests/generic/579

## Purpose

FS QA Test generic/579 Stress test for fs-verity. This tests enabling fs-verity on multiple files concurrently with concurrent readers on those files (with reads occurring before, during, and after the fs-verity enablement), while fsstress is also running on the same filesystem.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto stress verity`. It imports `./common/preamble`, `./common/filter`, `./common/verity`. Prerequisite and skip gates include `_require_scratch_verity`. Local helper functions: `_cleanup`. External command surfaces and helper binaries visible in the source include `fsstress`, `touch`, `wait`, `cp`, `sleep`, `grep`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `tmp`, `seq`, `TIME_FACTOR`, `LOAD_FACTOR`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch_verity`; `_disable_fsverity_signatures`; `_scratch_mkfs_verity &>> $seqres.full`; `_scratch_mount`; `nproc_enabler=$((4 * LOAD_FACTOR))`; `nproc_reader=$((6 * LOAD_FACTOR))`; `nproc_stress=$((3 * LOAD_FACTOR))`; `runtime=$((20 * TIME_FACTOR))`; `head -c $fsv_file_size /dev/urandom > $orig_file`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; uses explicit sync/fsync/remount points to force persistence boundaries. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

environmental skips and helper availability can dominate failures, so `_require_*` gates are part of the contract. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/579.out`; success is mostly silence after prerequisite and operation checks; grep-based checks assert expected metadata or data is still visible. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
