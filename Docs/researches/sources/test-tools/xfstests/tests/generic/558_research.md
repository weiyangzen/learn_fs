# sources/test-tools/xfstests/tests/generic/558

## Purpose

FS QA Test No. generic/558 Stress test fs by using up all inodes and check fs. Also a regression test for xfsprogs commit d586858 xfs_repair: fix sibling pointer tests in verify_dir2_path()

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto enospc`. It imports `./common/preamble`, `./common/filter`. Prerequisite and skip gates include `_require_inode_limits`, `_require_scratch`. Local helper functions: `create_file`. External command surfaces and helper binaries visible in the source include `df`, `feature`, `mkdir`, `wait`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `seq`, `LOAD_FACTOR`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_inode_limits`; `_require_scratch`; `echo "Silence is golden"`; `_scratch_mkfs_sized $((1024 * 1024 * 1024)) >>$seqres.full 2>&1`; `_scratch_mount`; `free_inodes=$(_get_free_inode $SCRATCH_MNT)`; `free_inodes=$(( ( (free_inodes + 999) / 1000) * 1000 ))`; `nr_cpus=$(( $($here/src/feature -o) * 4 * LOAD_FACTOR ))`; `echo "free inodes: $free_inodes nr_cpus: $nr_cpus" >> $seqres.full`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

environmental skips and helper availability can dominate failures, so `_require_*` gates are part of the contract. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/558.out`; success is mostly silence after prerequisite and operation checks. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
