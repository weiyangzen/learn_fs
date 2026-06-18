# sources/test-tools/xfstests/tests/generic/054

## Purpose

To test log replay with version 2 logs Initially keep this simple with just creates. In another qa test we can do more e.g. use fsstress.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest shutdown log v2log auto`. No local shell functions are declared. Key xfstests/helper interfaces include `_try_scratch_mount` (attempts to mount scratch and lets the test decide skip/fail behavior), `_check_scratch_fs` (runs scratch filesystem consistency checking), `_scratch_unmount` (unmounts scratch to force persistence checks), `_require_scratch` (requires a disposable scratch filesystem), `_scratch_mkfs` (formats the scratch filesystem). External or helper commands visible in the body include `ls`, `mkfs`, `mount`, `sync`, `touch`. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, `./common/log`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_require_scratch`; `_require_scratch_shutdown`; `_require_logstate`; `echo "*** init FS"`; `_scratch_unmount >/dev/null 2>&1`; `_scratch_mkfs >/dev/null 2>&1`; `_require_metadata_journaling $SCRATCH_DEV`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_logstate`, `_require_metadata_journaling`, `_require_scratch`, `_require_scratch_shutdown`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter`, `./common/log` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent, stress-tool behavior and kernel timing can expose nondeterminism. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: runs filesystem consistency checking; logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.
