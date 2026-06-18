# sources/test-tools/xfstests/tests/generic/563

## Purpose

This test verifies that cgroup aware writeback properly accounts I/Os in various scenarios. We perform reads/writes from different combinations of cgroups and verify that pages are accounted against the group that brought them into cache.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick`. It imports `./common/preamble`, `./common/filter`, `./common/cgroup2`. Prerequisite and skip gates include `_require_scratch_nocheck`, `_require_cgroup2 io`, `_require_loop`, `_require_block_device $SCRATCH_DEV`, `_require_non_zoned_device ${SCRATCH_DEV}`. Local helper functions: `_cleanup`, `check_cg`, `switch_cg`, `reset`. External command surfaces and helper binaries visible in the source include `xfs_io`, `seq`, `stat`, `grep`, `mkdir`, `umount`, `mount`. Important harness variables and paths include `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres.full`, `tmp`, `seq`, `FSTYP`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch_nocheck`; `_require_cgroup2 io`; `_require_loop`; `_require_block_device $SCRATCH_DEV`; `_require_non_zoned_device ${SCRATCH_DEV}`; `iosize=$((1024 * 1024 * 16))`; `loop_dev=$(_create_loop_device_like_bdev $SCRATCH_DEV $SCRATCH_DEV)`; `smajor=$((0x`stat -L -c %t $loop_dev`))`; `sminor=$((0x`stat -L -c %T $loop_dev`))`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; uses explicit sync/fsync/remount points to force persistence boundaries. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

environmental skips and helper availability can dominate failures, so `_require_*` gates are part of the contract. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/563.out`; grep-based checks assert expected metadata or data is still visible. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
