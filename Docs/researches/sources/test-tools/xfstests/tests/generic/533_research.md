# sources/test-tools/xfstests/tests/generic/533

## Purpose

FS QA Test No. 526. Simple attr smoke tests for user EAs, dereived from generic/097.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick attr`. It imports `./common/preamble`, `./common/attr`, `./common/filter`. Prerequisite and skip gates include `_require_test`, `_require_attrs`. Local helper functions: `getfattr`, `setfattr`. External command surfaces and helper binaries visible in the source include `setfattr`, `seq`, `touch`, `umount`, `mount`. Important harness variables and paths include `TEST_DIR`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_test`; `_require_attrs`; `echo -e "\ncreate file foo.$seq"`; `rm -f $file`; `touch $file`; `echo -e "\nshould be no EAs for foo.$seq:"`; `getfattr -d $file`; `echo -e "\nset EA <NOISE,woof>:"`; `setfattr -n user.NOISE -v woof $file`.

## State and Persistence Behavior

The test uses the configured test filesystem under `TEST_DIR` without necessarily reformatting it. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

environmental skips and helper availability can dominate failures, so `_require_*` gates are part of the contract. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/533.out`. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
