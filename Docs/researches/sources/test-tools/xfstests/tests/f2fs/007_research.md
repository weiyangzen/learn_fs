# sources/test-tools/xfstests/tests/f2fs/007

## Purpose

This is a regression test to check whether compressed metadata can become inconsistent after file compression, reservation releasement, and decompression.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `f2fs` suite. The harness entry and tags are `_begin_fstest auto quick rw compress`. No local shell functions are declared. Key xfstests/helper interfaces include `_check_scratch_fs` (runs scratch filesystem consistency checking), `_scratch_unmount` (unmounts scratch to force persistence checks), `_require_scratch` (requires a disposable scratch filesystem), `_scratch_mount` (mounts the scratch filesystem), `_scratch_mkfs` (formats the scratch filesystem). External or helper commands visible in the body include `fio`. Significant variables include `bs`, `status`, `testfile`.

## Control Flow

The script sources `./common/preamble`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_fixed_by_kernel_commit 26413ce18e85 \`; `_require_scratch`; `testfile_prefix=$SCRATCH_MNT/testfile`; `_require_fio $fio_config`; `_scratch_mkfs "-f -O extra_attr,compression" >> $seqres.full || _fail "mkfs failed"`; `_scratch_mount "-o compress_mode=user,compress_extension=*" >> $seqres.full`; `echo -e "Run fio to initialize file w/ specified compress ratio" >> $seqres.full`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state, compressed extents or clusters, fio verification state for direct/atomic I/O. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_fio`, `_require_scratch`. The test integrates with common xfstests libraries through `./common/preamble` and with suite-specific filesystem features selected by the `f2fs` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, stress-tool behavior and kernel timing can expose nondeterminism, compression heuristics may change block layout while preserving user data. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: runs filesystem consistency checking; logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.
