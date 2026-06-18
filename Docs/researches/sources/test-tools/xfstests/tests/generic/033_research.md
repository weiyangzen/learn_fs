# sources/test-tools/xfstests/tests/generic/033

## Purpose

This test stresses indirect block reservation for delayed allocation extents. XFS reserves extra blocks for deferred allocation of delalloc extents. These reserved blocks can be divided among more extents than anticipated if the original extent for which the blocks were reserved is split into multiple delalloc extents. If this scenario repeats, eventually some extents are left without any indirect block reservation whatsoever. This leads to assert failures and possibly other problems in XFS.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest auto quick rw zero`. No local shell functions are declared. Key xfstests/helper interfaces include `_require_xfs_io_command` (checks xfs_io subcommand support), `_scratch_cycle_mount` (unmounts and remounts scratch to test persisted metadata), `_require_scratch` (requires a disposable scratch filesystem), `_scratch_mount` (mounts the scratch filesystem), `_scratch_mkfs` (formats the scratch filesystem). No standalone external commands were extracted beyond shell builtins and xfstests helper calls.. Significant variables include `file`, `status`.

## Control Flow

The script sources `./common/preamble`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_require_scratch`; `_require_xfs_io_command "fzero"`; `_scratch_mkfs >/dev/null 2>&1`; `_scratch_mount`; `file=$SCRATCH_MNT/file.$seq`; `$XFS_IO_PROG -f -c "pwrite 0 $bytes" $file >> $seqres.full 2>&1`; `for i in $(seq 0 8192 $endoff); do`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_scratch`, `_require_xfs_io_command`. The test integrates with common xfstests libraries through `./common/preamble` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.
