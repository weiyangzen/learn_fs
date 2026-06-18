# sources/test-tools/xfstests/tests/generic/018

## Purpose

Basic defragmentation sanity tests

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest auto fsr quick defrag`. No local shell functions are declared. Key xfstests/helper interfaces include `_require_scratch` (requires a disposable scratch filesystem), `_require_defrag` (requires filesystem defrag support), `_scratch_mount` (mounts the scratch filesystem), `_scratch_mkfs` (formats the scratch filesystem). External or helper commands visible in the body include `defrag`, `rm`, `sync`, `touch`. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, `./common/defrag`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_require_scratch`; `_scratch_mkfs >/dev/null 2>&1`; `_scratch_mount`; `_require_defrag`; `fragfile=$SCRATCH_MNT/fragfile.$$`; `rm -f $fragfile`; `bsize=$(_get_file_block_size $SCRATCH_MNT)`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_defrag`, `_require_scratch`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter`, `./common/defrag` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.
