# sources/test-tools/xfstests/tests/generic/030

## Purpose

Test mapped writes against remap+truncate down/up to ensure we get the data correctly written. This can expose data corruption bugs on filesystems where the block size is smaller than the page size.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest auto quick rw mmap`. No local shell functions are declared. Key xfstests/helper interfaces include `_require_xfs_io_command` (checks xfs_io subcommand support), `_scratch_cycle_mount` (unmounts and remounts scratch to test persisted metadata), `_require_scratch` (requires a disposable scratch filesystem), `_scratch_mount` (mounts the scratch filesystem), `_filter_xfs_io` (normalizes xfs_io output). External or helper commands visible in the body include `rm`, `truncate`. Significant variables include `status`, `testfile`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_require_scratch`; `_require_xfs_io_command "mremap"`; `testfile=$SCRATCH_MNT/testfile`; `_scratch_mkfs > /dev/null 2>&1`; `_scratch_mount`; `$XFS_IO_PROG -t -f \`; `echo "==== Pre-Remount ==="`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_scratch`, `_require_xfs_io_command`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: passes when required commands complete and the xfstests golden output matches. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.
