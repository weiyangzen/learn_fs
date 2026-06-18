# sources/test-tools/xfstests/tests/generic/585

## Purpose

Regression test for: bc56ad8c74b8: ("xfs: Fix deadlock between AGI and AGF with RENAME_WHITEOUT")

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto rename`. It imports `./common/preamble`, `./common/filter`, `./common/renameat2`. Prerequisite and skip gates include `_require_scratch`, `_require_renameat2 whiteout`. No major local helper functions are defined; the scenario is driven directly by the top-level shell flow. External command surfaces and helper binaries visible in the source include `fsstress`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch`; `_require_renameat2 whiteout`; `_scratch_mkfs > $seqres.full 2>&1 || _fail "mkfs failed"`; `_scratch_mount >> $seqres.full 2>&1`; `_run_fsstress -z -n 150 -p 100 -f mknod=5 -f rwhiteout=5 -d $SCRATCH_MNT/fsstress`; `echo Silence is golden`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

environmental skips and helper availability can dominate failures, so `_require_*` gates are part of the contract. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/585.out`; success is mostly silence after prerequisite and operation checks. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
