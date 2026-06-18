# sources/test-tools/xfstests/tests/f2fs/018

## Purpose

This is a regression test to check whether page eof will be zero or not after we truncate partial data in compressed cluster.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `f2fs` suite. The harness entry and tags are `_begin_fstest auto quick rw compress`. Important local functions are `build_fio_config`, `check_data_eof`. Key xfstests/helper interfaces include `_require_xfs_io_command` (checks xfs_io subcommand support), `_require_scratch` (requires a disposable scratch filesystem), `_scratch_mount` (mounts the scratch filesystem), `_scratch_mkfs` (formats the scratch filesystem), `_require_fio` (checks fio support for generated job options). External or helper commands visible in the body include `rm`. Significant variables include `size`, `status`, `testfile`.

## Control Flow

The script sources `./common/preamble`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_fixed_by_kernel_commit ba8dac350faf \`; `_fixed_by_kernel_commit 0b2cd5092139 \`; `_require_xfs_io_command "truncate"`; `_require_scratch`; `testfile=$SCRATCH_MNT/testfile`; `_require_fio $fio_config`; `_scratch_mkfs "-O extra_attr,compression" >> $seqres.full || _fail "mkfs failed"`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state, compressed extents or clusters, fio verification state for direct/atomic I/O. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_fio`, `_require_scratch`, `_require_xfs_io_command`. The test integrates with common xfstests libraries through `./common/preamble` and with suite-specific filesystem features selected by the `f2fs` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent, stress-tool behavior and kernel timing can expose nondeterminism, compression heuristics may change block layout while preserving user data. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: prints `Silence is golden` after all checks pass; logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.
