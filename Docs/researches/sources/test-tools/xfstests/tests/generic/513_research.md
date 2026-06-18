# sources/test-tools/xfstests/tests/generic/513

## Purpose

Ensure that ctime is updated and capabilities are cleared when reflinking.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick clone`. It imports `./common/preamble`, `./common/filter`, `./common/reflink`, `./common/attr`. Prerequisite and skip gates include `_require_scratch_reflink`, `_require_command "$GETCAP_PROG" getcap`, `_require_command "$SETCAP_PROG" setcap`, `_require_attrs security`. No major local helper functions are defined; the scenario is driven directly by the top-level shell flow. External command surfaces and helper binaries visible in the source include `getcap`, `setcap`, `xfs_io`, `stat`, `sleep`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch_reflink`; `_require_command "$GETCAP_PROG" getcap`; `_require_command "$SETCAP_PROG" setcap`; `_require_attrs security`; `_scratch_mkfs >>$seqres.full 2>&1`; `_scratch_mount`; `$XFS_IO_PROG -f -c "pwrite -S 0x18 0 1m" $SCRATCH_MNT/foo >>$seqres.full`; `$XFS_IO_PROG -f -c "pwrite -S 0x20 0 1m" $SCRATCH_MNT/bar >>$seqres.full`; `$SETCAP_PROG cap_setgid,cap_setuid+ep $SCRATCH_MNT/bar`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

shared extent, COW, or dedupe paths can corrupt unrelated file ranges or violate swapfile restrictions. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/513.out`; success is mostly silence after prerequisite and operation checks. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
