# sources/test-tools/xfstests/tests/ext4/307

## Purpose

This ext4 test checks data integrity during defrag compaction by generating files with fsstress, recording md5 checksums, allocating a donor file, running e4compact, and validating every checksum after compacting.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `ext4` suite. The harness entry and tags are `_begin_fstest auto ioctl rw defrag prealloc`. Important local functions are `_workout`. Key xfstests/helper interfaces include `_require_xfs_io_command` (checks xfs_io subcommand support), `_scratch_mkfs_sized` (formats a scratch image/device of a requested size), `_require_scratch` (requires a disposable scratch filesystem), `_require_defrag` (requires filesystem defrag support), `_scratch_mount` (mounts the scratch filesystem). External or helper commands visible in the body include `awk`, `defrag`, `find`, `md5sum`. Significant variables include `FSSTRESS_AVOID`, `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, `./common/defrag`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_workout()`; `echo ""`; `echo "Run fsstress"`; `out=$SCRATCH_MNT/fsstress.$$`; `echo "fsstress $args" >> $seqres.full`; `_run_fsstress $args`; `echo "Allocate donor file"`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_defrag`, `_require_scratch`, `_require_xfs_io_command`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter`, `./common/defrag` and with suite-specific filesystem features selected by the `ext4` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent, stress-tool behavior and kernel timing can expose nondeterminism. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: uses checksums to detect data changes; logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.
