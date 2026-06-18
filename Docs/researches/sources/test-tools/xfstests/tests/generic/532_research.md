# sources/test-tools/xfstests/tests/generic/532

## Purpose

Regression test for a bug where XFS fails to set statx attributes_mask but sets attribute flags anyway, which is fixed by commit 1b9598c8fb99 ("xfs: fix reporting supported extra file attributes for statx()")

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick`. It imports `./common/preamble`. Prerequisite and skip gates include `_require_test`. Local helper functions: `_cleanup`, `get_attributes`, `get_attributes_mask`, `check_statx_attributes`. External command surfaces and helper binaries visible in the source include `xfs_io`, `chattr`, `grep`, `stat`, `seq`, `touch`. Important harness variables and paths include `TEST_DIR`, `seqres.full`, `tmp`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_test`; `echo "Silence is golden"`; `touch $testfile`; `check_statx_attributes`; `check_statx_attributes`; `$CHATTR_PROG -i $testfile`; `check_statx_attributes`; `$CHATTR_PROG -a $testfile`.

## State and Persistence Behavior

The test uses the configured test filesystem under `TEST_DIR` without necessarily reformatting it. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

environmental skips and helper availability can dominate failures, so `_require_*` gates are part of the contract. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/532.out`; success is mostly silence after prerequisite and operation checks; grep-based checks assert expected metadata or data is still visible. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
