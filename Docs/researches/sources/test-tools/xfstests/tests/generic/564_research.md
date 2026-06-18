# sources/test-tools/xfstests/tests/generic/564

## Purpose

Exercise copy_file_range() syscall error conditions. This is a regression test for kernel commit: 96e6e8f4a68d ("vfs: add missing checks to copy_file_range")

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick copy_range`. It imports `./common/preamble`, `./common/filter`. Prerequisite and skip gates include `_require_test`, `_require_loop`, `_require_mknod`, `_require_xfs_io_command "copy_range"`, `_require_xfs_io_command "copy_range" "-f"`. Local helper functions: `_cleanup`, `do_rlimit_copy`. External command surfaces and helper binaries visible in the source include `xfs_io`, `seq`, `mkdir`, `truncate`, `grep`. Important harness variables and paths include `TEST_DIR`, `seqres.full`, `tmp`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_register_cleanup "_cleanup" BUS`; `_require_test`; `_require_loop`; `_require_mknod`; `_require_xfs_io_command "copy_range"`; `_require_xfs_io_command "copy_range" "-f"`; `rm -rf $testdir`; `mkdir $testdir`; `$XFS_IO_PROG -f -c "pwrite -S 0x61 0 128k" $testdir/file >> $seqres.full 2>&1`.

## State and Persistence Behavior

The test uses the configured test filesystem under `TEST_DIR` without necessarily reformatting it. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

environmental skips and helper availability can dominate failures, so `_require_*` gates are part of the contract. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/564.out`; grep-based checks assert expected metadata or data is still visible. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
