# sources/test-tools/xfstests/tests/generic/491

## Purpose

Test first read with freeze right after mount. With ext4, this leads to freeze proection bypass WARN_ON in ext4_journal_check_start.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick freeze mount`. It imports `./common/preamble`, `./common/filter`. Prerequisite and skip gates include `_require_scratch`, `_require_freeze`, `_require_command "$TIMEOUT_PROG" "timeout"`. Local helper functions: `_cleanup`. External command surfaces and helper binaries visible in the source include `timeout`, `mount`, `xfs_freeze`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `tmp`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch`; `_require_freeze`; `_require_command "$TIMEOUT_PROG" "timeout"`; `_scratch_mkfs >>$seqres.full 2>&1`; `_scratch_mount`; `echo "frozen" > $testfile`; `_scratch_cycle_mount "noatime"`; `xfs_freeze -f $SCRATCH_MNT`; `$TIMEOUT_PROG -s KILL 5s cat $testfile`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

environmental skips and helper availability can dominate failures, so `_require_*` gates are part of the contract. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/491.out`. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
