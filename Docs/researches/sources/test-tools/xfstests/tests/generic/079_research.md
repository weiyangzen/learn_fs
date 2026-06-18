# sources/test-tools/xfstests/tests/generic/079

## Purpose

Run the t_immutable test program for immutable/append-only files.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest auto quick ioctl metadata`. Important local functions are `_cleanup`. Key xfstests/helper interfaces include `_require_test_program` (checks availability of an xfstests helper binary), `_require_scratch` (requires a disposable scratch filesystem), `_scratch_mount` (mounts the scratch filesystem), `_scratch_mkfs` (formats the scratch filesystem). External or helper commands visible in the body include `grep`, `rm`. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, `./common/attr`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_cleanup()`; `echo "*** cleaning up"`; `$timmutable -r $SCRATCH_MNT/$seq`; `_require_chattr ia`; `_require_user_exists "nobody"`; `_require_user_exists "daemon"`; `_require_test_program "t_immutable"`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_chattr`, `_require_scratch`, `_require_test_program`, `_require_user_exists`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter`, `./common/attr` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: passes when required commands complete and the xfstests golden output matches. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.
