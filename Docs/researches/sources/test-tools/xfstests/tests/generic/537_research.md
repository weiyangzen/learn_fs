# sources/test-tools/xfstests/tests/generic/537

## Purpose

Ensure that we can't call fstrim on filesystems mounted norecovery, because FSTRIM implementations use free space metadata to drive the discard requests and we told the filesystem not to make sure the metadata are up to date. The following patches fixed the bug on ext4, xfs and btrfs ext4: prohibit fstrim in norecovery mode xfs: prohibit fstrim in norecovery mode Btrfs: do not allow trimming when a fs is mounted with the nologreplay option

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick trim`. It imports `./common/preamble`, `./common/filter`, `./common/quota`. Prerequisite and skip gates include `_require_scratch`, `_require_fstrim`, `_require_metadata_journaling $SCRATCH_DEV`. No major local helper functions are defined; the scenario is driven directly by the top-level shell flow. External command surfaces and helper binaries visible in the source include `fstrim`, `mount`. Important harness variables and paths include `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres.full`, `seq`, `FSTYP`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch`; `_require_fstrim`; `_scratch_mkfs > $seqres.full 2>&1`; `_require_metadata_journaling $SCRATCH_DEV`; `echo "fstrim on regular mount"`; `_scratch_mount >> $seqres.full 2>&1`; `$FSTRIM_PROG -v $SCRATCH_MNT >> $seqres.full 2>&1 || _notrun "FSTRIM not supported"`; `_scratch_unmount`; `echo "fstrim on ro mount"`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; enables quota accounting/enforcement state and adjusts grace timers or ownership/project metadata. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

environmental skips and helper availability can dominate failures, so `_require_*` gates are part of the contract. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/537.out`; grep-based checks assert expected metadata or data is still visible. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
