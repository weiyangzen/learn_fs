# sources/test-tools/xfstests/tests/generic/566

## Purpose

Regression test for chgrp returning to userspace with ILOCK held after a hard quota error. This causes the filesystem to hang if kernel is not patched. This test goes with commit 1fb254aa983bf ("xfs: fix missing ILOCK unlock when xfs_setattr_nonsize fails due to EDQUOT")

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick quota metadata`. It imports `./common/preamble`, `./common/quota`, `./common/filter`. Prerequisite and skip gates include `_require_scratch`, `_require_quota`, `_require_xfs_quota_foreign`, `_require_user`. Local helper functions: `_cleanup`. External command surfaces and helper binaries visible in the source include `xfs_quota`, `xfs_io`, `chgrp`, `mkdir`, `chown`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch`; `_require_quota`; `_require_xfs_quota_foreign`; `_require_user`; `_qmount_option "grpquota"`; `_scratch_mkfs > $seqres.full`; `_qmount`; `mkdir -p $dir`; `chown $qa_user $dir`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; enables quota accounting/enforcement state and adjusts grace timers or ownership/project metadata. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

quota timer and enforcement semantics vary by filesystem and userspace quota tooling. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/566.out`. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
