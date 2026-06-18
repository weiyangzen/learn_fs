# sources/test-tools/xfstests/tests/generic/053

## Purpose

xfs_repair breaks acls

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest acl repair auto quick`. Important local functions are `list_acls`. Key xfstests/helper interfaces include `_try_scratch_mount` (attempts to mount scratch and lets the test decide skip/fail behavior), `_check_scratch_fs` (runs scratch filesystem consistency checking), `_require_scratch` (requires a disposable scratch filesystem), `_scratch_mkfs` (formats the scratch filesystem). External or helper commands visible in the body include `sed`. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, `./common/attr`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_require_scratch`; `_require_acls`; `_acl_setup_ids`; `_do_die_on_error=y`; `test=$SCRATCH_MNT/test`; `_do 'make filesystem on $SCRATCH_DEV' '_scratch_mkfs'`; `_do 'mount filesytem' '_try_scratch_mount'`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_acls`, `_require_scratch`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter`, `./common/attr` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: runs filesystem consistency checking. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.
