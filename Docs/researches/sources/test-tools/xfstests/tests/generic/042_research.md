# sources/test-tools/xfstests/tests/generic/042

## Purpose

Test stale data exposure via writeback using various file allocation modification commands. The presumption is that such commands result in partial writeback and can convert a delayed allocation extent, that might be larger than the ranged affected by fallocate, to a normal extent. If the fs happens to crash sometime between when the extent modification is logged and writeback occurs for dirty pages within the extent but outside of the fallocated range, stale data exposure can occur.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest shutdown rw punch zero prealloc auto quick`. Important local functions are `_crashtest`. Key xfstests/helper interfaces include `_require_xfs_io_command` (checks xfs_io subcommand support), `_require_scratch` (requires a disposable scratch filesystem), `_scratch_mount` (mounts the scratch filesystem), `_filter_xfs_io` (normalizes xfs_io output), `_scratch_mkfs` (formats the scratch filesystem). External or helper commands visible in the body include `grep`, `mkdir`, `od`. Significant variables include `file`, `size`, `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, `./common/punch`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_crashtest()`; `img=$SCRATCH_MNT/$seq.img`; `mnt=$SCRATCH_MNT/$seq.mnt`; `$XFS_IO_PROG -f -c "truncate 0" -c "pwrite -S 0xCD 0 $size" $img \`; `_mkfs_dev $img >> $seqres.full 2>&1`; `mkdir -p $mnt`; `_mount $img $mnt`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_local_device`, `_require_metadata_journaling`, `_require_scratch`, `_require_scratch_shutdown`, `_require_xfs_io_command`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter`, `./common/punch` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.
