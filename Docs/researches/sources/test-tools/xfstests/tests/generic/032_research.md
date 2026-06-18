# sources/test-tools/xfstests/tests/generic/032

## Purpose

This test implements a data corruption scenario on XFS filesystems with sub-page sized blocks and unwritten extents. Inode lock contention during writeback of pages to unwritten extents leads to failure to convert those extents on I/O completion. This causes data corruption as unwritten extents are always read back as zeroes.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest auto quick rw fiemap prealloc`. Important local functions are `_cleanup`, `_syncloop`. Key xfstests/helper interfaces include `_require_xfs_io_command` (checks xfs_io subcommand support), `_scratch_cycle_mount` (unmounts and remounts scratch to test persisted metadata), `_require_scratch` (requires a disposable scratch filesystem), `_scratch_mount` (mounts the scratch filesystem), `_filter_fiemap` (normalizes fiemap output). External or helper commands visible in the body include `awk`, `fiemap`, `grep`, `rm`. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, `./common/punch`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_cleanup()`; `rm -f $tmp.*`; `_syncloop()`; `while [ true ]; do`; `_scratch_sync`; `_require_scratch`; `_require_xfs_io_command "falloc"`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_scratch`, `_require_xfs_io_command`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/punch` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent, extent layout assumptions can vary by filesystem feature and kernel version. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.
