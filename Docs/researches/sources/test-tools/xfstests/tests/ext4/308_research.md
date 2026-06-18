# sources/test-tools/xfstests/tests/ext4/308

## Purpose

This ext4 test checks both data integrity and layout stability during e4compact. It creates fragmented preallocated files, records fiemap layout and md5 sums, runs compacting twice, and expects the second EXT4_IOC_MOVE_EXT pass to restore the original layout.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `ext4` suite. The harness entry and tags are `_begin_fstest auto ioctl rw prealloc quick defrag fiemap`. Important local functions are `_workout`. Key xfstests/helper interfaces include `_require_xfs_io_command` (checks xfs_io subcommand support), `_require_scratch` (requires a disposable scratch filesystem), `_filter_scratch` (normalizes scratch paths in stdout), `_require_defrag` (requires filesystem defrag support), `_scratch_mount` (mounts the scratch filesystem). External or helper commands visible in the body include `defrag`, `diff`, `fiemap`, `ls`, `md5sum`. Significant variables include `PIDS`, `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, `./common/defrag`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_require_scratch`; `_require_defrag`; `_require_xfs_io_command "falloc"`; `_workout()`; `echo "Create file with $nr * 2 fragments"`; `for ((i=0;i<nr;i++))`; `$XFS_IO_PROG -f -c "falloc $((409600*i)) 4k"  \`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_defrag`, `_require_scratch`, `_require_xfs_io_command`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter`, `./common/defrag` and with suite-specific filesystem features selected by the `ext4` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent, extent layout assumptions can vary by filesystem feature and kernel version. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: uses byte-for-byte comparison of generated and expected data; uses checksums to detect data changes; logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.
