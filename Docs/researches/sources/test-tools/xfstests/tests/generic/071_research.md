# sources/test-tools/xfstests/tests/generic/071

## Purpose

Test extent pre-allocation (using fallocate) into a region that already has a pre-allocated extent that ends beyond the file's size. Verify that if the fs is unmounted immediately after, the file's size and content are not lost.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest auto quick prealloc`. No local shell functions are declared. Key xfstests/helper interfaces include `_require_xfs_io_command` (checks xfs_io subcommand support), `_scratch_cycle_mount` (unmounts and remounts scratch to test persisted metadata), `_require_scratch` (requires a disposable scratch filesystem), `_scratch_mount` (mounts the scratch filesystem), `_filter_xfs_io` (normalizes xfs_io output). External or helper commands visible in the body include `od`. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_require_scratch`; `_require_xfs_io_command "falloc" "-k"`; `_scratch_mkfs >> $seqres.full 2>&1`; `_scratch_mount`; `$XFS_IO_PROG -f -c "falloc -k 0 1M" $SCRATCH_MNT/foo`; `$XFS_IO_PROG -c "pwrite -S 0xaa 0 256K" $SCRATCH_MNT/foo | _filter_xfs_io`; `$XFS_IO_PROG -c "falloc 0 512K" $SCRATCH_MNT/foo`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_scratch`, `_require_xfs_io_command`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.
