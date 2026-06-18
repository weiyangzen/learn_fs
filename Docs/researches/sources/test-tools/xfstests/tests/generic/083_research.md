# sources/test-tools/xfstests/tests/generic/083

## Purpose

Exercise filesystem full behaviour - run numerous fsstress processes in write mode on a small filesystem. NB: delayed allocate flushing is quite deadlock prone at the filesystem full boundary due to the fact that we will retry allocation several times after flushing, before giving back ENOSPC. Note that this test will intentionally cause console msgs of form: dksc0d1s4: Process [fsstress] ran out of disk space dksc0d1s4: Process [fsstress] ran out of disk space dksc0d1s4: Process [fsstress] ran out of disk space

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest rw auto enospc stress`. Important local functions are `workout`. Key xfstests/helper interfaces include `_scratch_mkfs_sized` (formats a scratch image/device of a requested size), `_scratch_unmount` (unmounts scratch to force persistence checks), `_require_scratch` (requires a disposable scratch filesystem), `_scratch_mount` (mounts the scratch filesystem). External or helper commands visible in the body include `mkfs`. Significant variables include `FSSTRESS_ARGS`, `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_require_scratch`; `_require_no_large_scratch_dev`; `_scratch_unmount >/dev/null 2>&1`; `echo "*** mkfs -dsize=$fsz,agcount=$ags"    >>$seqres.full`; `echo ""                                     >>$seqres.full`; `if [ $FSTYP = xfs ]`; `_scratch_mkfs_xfs -dsize=$fsz,agcount=$ags  >>$seqres.full 2>&1`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_no_large_scratch_dev`, `_require_scratch`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent, stress-tool behavior and kernel timing can expose nondeterminism. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.
