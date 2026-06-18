# sources/test-tools/xfstests/tests/generic/608

## Purpose

FS QA Test 608 Toggling FS_XFLAG_DAX on an existing file can make S_DAX on the file change immediately when all applications close the file. It's a regression test for: 'commit 77573fa310d9 ("fs: Kill DCACHE_DONTCACHE dentry even if DCACHE_REFERENCED is set")' Write data into a file and then enable DAX on the file immediately, the written data which is still in the buffer should be synchronized to disk instead of discarded when the corresponding inode is evicted. It's a regression test for: 'commit 88149082bb8e ("fs: Handle I_DONTCACHE in iput_final() instead of generic_drop_inode()"'

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto attr quick dax`. It imports `./common/preamble`, `./common/filter`. Prerequisite and skip gates include `_require_scratch_dax_mountopt "dax=always"`, `_require_dax_iflag`, `_require_xfs_io_command "lsattr" "-v"`, `_require_xfs_io_command "statx" "-r"`. Local helper functions: `test_enable_dax`, `test_disable_dax`, `test_buffered_data_lost`, `do_tests`. External command surfaces and helper binaries visible in the source include `xfs_io`, `touch`, `mkdir`, `grep`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `seq`, `MOUNT_OPTIONS`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch_dax_mountopt "dax=always"`; `_require_dax_iflag`; `_require_xfs_io_command "lsattr" "-v"`; `_require_xfs_io_command "statx" "-r"`; `_scratch_mkfs >> $seqres.full 2>&1`; `export MOUNT_OPTIONS=""`; `echo "Silence is golden"`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; uses explicit sync/fsync/remount points to force persistence boundaries; depends on per-inode or mount-option DAX state visible through xattrs/statx and mmap/direct-I/O behavior. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

DAX mount options, inode flags, page-cache invalidation, and statx reporting have filesystem-specific behavior. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/608.out`; success is mostly silence after prerequisite and operation checks; grep-based checks assert expected metadata or data is still visible. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
