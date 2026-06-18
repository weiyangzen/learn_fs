# sources/test-tools/xfstests/tests/ext4/302

## Purpose

This ext4 defragmentation stress test defragments a buffered-I/O target file while a separate direct-I/O fio job writes the donor file and a verifier job checks the target. It stresses donor-file interaction, EBUSY handling, and data verification during e4defrag.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `ext4` suite. The harness entry and tags are `_begin_fstest aio auto ioctl rw stress defrag`. Important local functions are `_workout`. Key xfstests/helper interfaces include `_scratch_unmount` (unmounts scratch to force persistence checks), `_require_scratch` (requires a disposable scratch filesystem), `_require_odirect` (requires O_DIRECT support), `_require_defrag` (requires filesystem defrag support), `_scratch_mount` (mounts the scratch filesystem). External or helper commands visible in the body include `blockdev`, `defrag`. Significant variables include `BLK_DEV_SIZE`, `FILE_SIZE`, `bs`, `size`, `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, `./common/defrag`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_exclude_fs ext2`; `_exclude_fs ext3`; `_require_scratch`; `_require_defrag`; `_require_odirect`; `BLK_DEV_SIZE=\`blockdev --getsz $SCRATCH_DEV\``; `_workout()`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state, fio verification state for direct/atomic I/O. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_defrag`, `_require_fio`, `_require_odirect`, `_require_scratch`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter`, `./common/defrag` and with suite-specific filesystem features selected by the `ext4` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent, stress-tool behavior and kernel timing can expose nondeterminism. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.
