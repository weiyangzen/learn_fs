# sources/test-tools/xfstests/tests/generic/027

## Purpose

Run 8 processes writing 1k files to seperate files in seperate dirs to hit ENOSPC on small fs with little free space. Loop for 100 iterations. Regression test for 34cf865 ext4: fix deadlock when writing in ENOSPC conditions

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest auto enospc`. Important local functions are `create_file`. Key xfstests/helper interfaces include `_scratch_mkfs_sized` (formats a scratch image/device of a requested size), `_scratch_unmount` (unmounts scratch to force persistence checks), `_require_scratch` (requires a disposable scratch filesystem), `_scratch_mount` (mounts the scratch filesystem). External or helper commands visible in the body include `mkdir`, `rm`. Significant variables include `dir`, `loop`, `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `mkdir -p $dir >/dev/null 2>&1`; `while $XFS_IO_PROG -f $direct -c "pwrite 0 1k" $dir/file_$i >/dev/null 2>&1; do`; `_require_scratch`; `_require_no_compress`; `echo "Silence is golden"`; `_scratch_mkfs_sized $((256 * 1024 * 1024)) >>$seqres.full 2>&1`; `_scratch_mount`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state, compressed extents or clusters. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_no_compress`, `_require_scratch`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent, compression heuristics may change block layout while preserving user data. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: prints `Silence is golden` after all checks pass; logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.
