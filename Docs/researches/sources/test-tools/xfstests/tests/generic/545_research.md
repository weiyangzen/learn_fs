# sources/test-tools/xfstests/tests/generic/545

## Purpose

Check that we can't set the FS_APPEND_FL and FS_IMMUTABLE_FL inode flags without capbility CAP_LINUX_IMMUTABLE

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick cap`. It imports `./common/preamble`, `./common/filter`, `./common/attr`. Prerequisite and skip gates include `_require_test`, `_require_chattr i`, `_require_chattr a`, `_require_command "$CAPSH_PROG" "capsh"`. Local helper functions: `_cleanup`, `do_filter_output`. External command surfaces and helper binaries visible in the source include `chattr`, `capsh`, `seq`, `mkdir`, `touch`, `grep`. Important harness variables and paths include `TEST_DIR`, `tmp`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_test`; `_require_chattr i`; `_require_chattr a`; `_require_command "$CAPSH_PROG" "capsh"`; `rm -rf $workdir`; `mkdir $workdir`; `echo "Create the original files"`; `touch $workdir/file1`; `touch $workdir/file2`.

## State and Persistence Behavior

The test uses the configured test filesystem under `TEST_DIR` without necessarily reformatting it. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

environmental skips and helper availability can dominate failures, so `_require_*` gates are part of the contract. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/545.out`; grep-based checks assert expected metadata or data is still visible. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
