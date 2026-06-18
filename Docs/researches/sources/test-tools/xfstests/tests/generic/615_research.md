# sources/test-tools/xfstests/tests/generic/615

## Purpose

Test that if we keep overwriting an entire file, either with buffered writes or direct IO writes, the number of used blocks reported by stat(2) is never zero while writeback is in progress.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick rw`. It imports `./common/preamble`, `./common/filter`. Prerequisite and skip gates include `_require_scratch`, `_require_odirect`. Local helper functions: `stat_loop`. External command surfaces and helper binaries visible in the source include `xfs_io`, `stat`, `touch`, `kill`, `wait`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `tmp`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch`; `_require_odirect`; `_scratch_mkfs >>$seqres.full 2>&1`; `_scratch_mount`; `$XFS_IO_PROG -f -s -c "pwrite -b 64K 0 64K" $SCRATCH_MNT/foo > /dev/null`; `touch $loop_file`; `stat_loop $SCRATCH_MNT/foo &`; `echo "Testing buffered writes"`; `break`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

I/O path races may be timing-sensitive and surface only under mmap, direct I/O, io_uring, or fsx replay stress. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/615.out`. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
