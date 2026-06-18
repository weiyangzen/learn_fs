# sources/test-tools/xfstests/tests/generic/606

## Purpose

By the following cases, verify if statx() can query S_DAX flag on regular file correctly. 1) With dax=always option, FS_XFLAG_DAX is ignored and S_DAX flag always exists on regular file. 2) With dax=inode option, setting/clearing FS_XFLAG_DAX can change S_DAX flag on regular file. 3) With dax=never option, FS_XFLAG_DAX is ignored and S_DAX flag never exists on regular file.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto attr quick dax`. It imports `./common/preamble`, `./common/filter`. Prerequisite and skip gates include `_require_scratch_dax_mountopt "dax=always"`, `_require_dax_iflag`, `_require_xfs_io_command "statx" "-r"`. Local helper functions: `test_s_dax`, `do_tests`. External command surfaces and helper binaries visible in the source include `xfs_io`, `mkdir`, `touch`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `seq`, `MOUNT_OPTIONS`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch_dax_mountopt "dax=always"`; `_require_dax_iflag`; `_require_xfs_io_command "statx" "-r"`; `echo "Silence is golden"`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; depends on per-inode or mount-option DAX state visible through xattrs/statx and mmap/direct-I/O behavior. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

DAX mount options, inode flags, page-cache invalidation, and statx reporting have filesystem-specific behavior. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/606.out`; success is mostly silence after prerequisite and operation checks. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
