# sources/test-tools/xfstests/tests/f2fs/006

## Purpose

This is a regression test to check whether f2fs handles dirty data correctly when checkpoint is disabled, if lfs mode is on, it will trigger OPU for all overwritten data, this will cost free segments, so f2fs must account overwritten data as OPU data when calculating free space, otherwise, it may run out of free segments in f2fs' allocation function. If kernel config CONFIG_F2FS_CHECK_FS is on, it will cause system panic, otherwise, dd may encounter I/O error.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `f2fs` suite. The harness entry and tags are `_begin_fstest auto quick`. No local shell functions are declared. Key xfstests/helper interfaces include `_scratch_mkfs_sized` (formats a scratch image/device of a requested size), `_require_scratch` (requires a disposable scratch filesystem), `_scratch_mount` (mounts the scratch filesystem). External or helper commands visible in the body include `dd`. Significant variables include `status`, `testfile`.

## Control Flow

The script sources `./common/preamble`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_fixed_by_kernel_commit 1acd73edbbfe \`; `_require_scratch`; `_scratch_mkfs_sized $((1024*1024*100)) >> $seqres.full`; `_scratch_mount -o mode=lfs,checkpoint=disable:10%,noinline_dentry >> $seqres.full`; `testfile=$SCRATCH_MNT/testfile`; `dd if=/dev/zero of=$testfile bs=1M count=50 2>/dev/null`; `dd if=/dev/zero of=$testfile bs=1M count=50 conv=notrunc conv=fsync >>$seqres.full 2>&1`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_scratch`. The test integrates with common xfstests libraries through `./common/preamble` and with suite-specific filesystem features selected by the `f2fs` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: prints `Silence is golden` after all checks pass; logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.
