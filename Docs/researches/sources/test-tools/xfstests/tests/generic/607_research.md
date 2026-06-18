# sources/test-tools/xfstests/tests/generic/607

## Purpose

Verify the inheritance behavior of FS_XFLAG_DAX flag in various combinations. 1) New files and directories automatically inherit FS_XFLAG_DAX from their parent directory. 2) cp operation make files and directories inherit the FS_XFLAG_DAX from new parent directory. 3) mv operation make files and directories preserve the FS_XFLAG_DAX from old parent directory. In addition, setting/clearing FS_XFLAG_DAX flag is not impacted by dax mount options.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto attr quick dax`. It imports `./common/preamble`, `./common/filter`. Prerequisite and skip gates include `_require_scratch`, `_require_dax_iflag`, `_require_xfs_io_command "lsattr" "-v"`. Local helper functions: `test_xflag_inheritance1`, `test_xflag_inheritance2`, `test_xflag_inheritance3`, `test_xflag_inheritance4`, `test_xflag_inheritance5`, `do_xflag_tests`, `do_tests`. External command surfaces and helper binaries visible in the source include `xfs_io`, `cp`, `mv`, `mount`, `grep`, `mkdir`, `touch`, `seq`. Important harness variables and paths include `SCRATCH_MNT`, `TEST_DIR`, `seqres.full`, `seq`, `FSTYP`, `MOUNT_OPTIONS`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch`; `_require_dax_iflag`; `_require_xfs_io_command "lsattr" "-v"`; `output="$($XFS_IO_PROG -c "lsattr -v" $TEST_DIR 2>&1)"`; `echo "$output" | grep -q "Inappropriate ioctl for device" && _notrun "$FSTYP: FSGETXATTR not supported on directories."`; `echo "Silence is golden"`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; uses the configured test filesystem under `TEST_DIR` without necessarily reformatting it; depends on per-inode or mount-option DAX state visible through xattrs/statx and mmap/direct-I/O behavior. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

DAX mount options, inode flags, page-cache invalidation, and statx reporting have filesystem-specific behavior. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/607.out`; success is mostly silence after prerequisite and operation checks; grep-based checks assert expected metadata or data is still visible. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
