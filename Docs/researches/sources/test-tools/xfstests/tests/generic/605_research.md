# sources/test-tools/xfstests/tests/generic/605

## Purpose

Test per-inode DAX flag by mmap direct/buffered IO.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto attr quick dax prealloc mmap`. It imports `./common/preamble`, `./common/filter`. Prerequisite and skip gates include `_require_hugepages`, `_require_scratch_dax_mountopt "dax=always"`, `_require_test_program "feature"`, `_require_test_program "t_mmap_dio"`, `_require_dax_iflag`, `_require_xfs_io_command "falloc"`. Local helper functions: `prep_directories`, `prep_files`, `t_both_dax`, `t_nondax_to_dax`, `t_dax_to_nondax`, `t_both_nondax`, `t_dax_flag_mmap_dio`, `do_tests`. External command surfaces and helper binaries visible in the source include `xfs_io`, `t_mmap_dio`, `feature`, `mkdir`, `mount`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `seq`, `MOUNT_OPTIONS`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_hugepages`; `_require_scratch_dax_mountopt "dax=always"`; `_require_test_program "feature"`; `_require_test_program "t_mmap_dio"`; `_require_dax_iflag`; `_require_xfs_io_command "falloc"`; `_scratch_mkfs_geom $(_get_hugepagesize) 1 >> $seqres.full 2>&1`; `tsize=$((128 * 1024 * 1024))`; `export MOUNT_OPTIONS=""`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; depends on per-inode or mount-option DAX state visible through xattrs/statx and mmap/direct-I/O behavior. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

I/O path races may be timing-sensitive and surface only under mmap, direct I/O, io_uring, or fsx replay stress; DAX mount options, inode flags, page-cache invalidation, and statx reporting have filesystem-specific behavior. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/605.out`; success is mostly silence after prerequisite and operation checks. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
