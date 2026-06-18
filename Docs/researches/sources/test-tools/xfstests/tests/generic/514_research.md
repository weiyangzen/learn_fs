# sources/test-tools/xfstests/tests/generic/514

## Purpose

Ensure that file size resource limits are respected when reflinking.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick clone`. It imports `./common/preamble`, `./common/filter`, `./common/reflink`. Prerequisite and skip gates include `_require_scratch_reflink`, `_require_user`. No major local helper functions are defined; the scenario is driven directly by the top-level shell flow. External command surfaces and helper binaries visible in the source include `xfs_io`, `chmod`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch_reflink`; `_require_user`; `_scratch_mkfs >>$seqres.full 2>&1`; `_scratch_mount`; `chmod a+rwx $SCRATCH_MNT`; `$XFS_IO_PROG -f -c "pwrite -S 0x18 0 1m" $SCRATCH_MNT/foo >>$seqres.full`; `_su -s/bin/bash - $qa_user -c "ulimit -f 64 ; $XFS_IO_PROG -f -c \"reflink $SCRATCH_MNT/foo\" $SCRATCH_MNT/bar" >> $seqres.full 2>&1`; `sz="$(_get_filesize $SCRATCH_MNT/bar)"`; `echo "Oddball file size $sz??"`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

shared extent, COW, or dedupe paths can corrupt unrelated file ranges or violate swapfile restrictions. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/514.out`; success is mostly silence after prerequisite and operation checks; content dumps/hexdumps expose corruption or unexpected nonzero data. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
