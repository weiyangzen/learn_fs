# sources/test-tools/xfstests/tests/generic/588

## Purpose

Test that if we clone part of an extent from a file to itself at different offset, fsync it, rewrite (COW) part of the extent from the former offset, fsync it again, power fail and then mount the filesystem, we are able to read the whole file and it has the correct data.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick log clone`. It imports `./common/preamble`, `./common/filter`, `./common/reflink`, `./common/dmflakey`. Prerequisite and skip gates include `_require_scratch_reflink`, `_require_dm_target flakey`, `_require_metadata_journaling $SCRATCH_DEV`, `_require_congruent_file_oplen $SCRATCH_MNT 65536`. Local helper functions: `_cleanup`. External command surfaces and helper binaries visible in the source include `xfs_io`, `mount`. Important harness variables and paths include `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres.full`, `tmp`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch_reflink`; `_require_dm_target flakey`; `_scratch_mkfs >>$seqres.full 2>&1`; `_require_metadata_journaling $SCRATCH_DEV`; `_init_flakey`; `_scratch_mount`; `_require_congruent_file_oplen $SCRATCH_MNT 65536`; `$XFS_IO_PROG -f -c "pwrite -S 0xa3 0 256K" -c "fsync" -c "pwrite -S 0xc7 256K 256K" $SCRATCH_MNT/foobar | _filter_xfs_io`; `$XFS_IO_PROG -c "reflink $SCRATCH_MNT/foobar 320K 0K 64K" -c "fsync" $SCRATCH_MNT/foobar | _filter_xfs_io`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; injects block-device, power-fail, shutdown, or thin-provisioning behavior to validate recovery paths; uses explicit sync/fsync/remount points to force persistence boundaries. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

ordering bugs in journal replay or fsync logging can lose metadata or data after simulated power loss; shared extent, COW, or dedupe paths can corrupt unrelated file ranges or violate swapfile restrictions. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/588.out`. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
