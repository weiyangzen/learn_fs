# sources/test-tools/xfstests/tests/generic/601

## Purpose

Test individual user ID quota grace period extension This is the xfs_quota version of the test This test only exercises user quota because it's not known whether the filesystem can set individual grace timers for each quota type

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick quota`. It imports `./common/preamble`, `./common/filter`, `./common/quota`. Prerequisite and skip gates include `_require_scratch`, `_require_quota`, `_require_user`, `_require_xfs_quota_foreign`, `_require_setquota_project`. No major local helper functions are defined; the scenario is driven directly by the top-level shell flow. External command surfaces and helper binaries visible in the source include `xfs_quota`, `setquota`, `grep`, `touch`, `sleep`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch`; `_require_quota`; `_require_user`; `_require_xfs_quota_foreign`; `_require_setquota_project`; `_scratch_mkfs >$seqres.full 2>&1`; `_qmount_option "usrquota"`; `_qmount`; `echo "Silence is golden"`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; enables quota accounting/enforcement state and adjusts grace timers or ownership/project metadata. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

quota timer and enforcement semantics vary by filesystem and userspace quota tooling. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/601.out`; success is mostly silence after prerequisite and operation checks; content dumps/hexdumps expose corruption or unexpected nonzero data; grep-based checks assert expected metadata or data is still visible. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
