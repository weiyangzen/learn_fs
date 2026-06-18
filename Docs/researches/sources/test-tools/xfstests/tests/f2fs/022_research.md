# sources/test-tools/xfstests/tests/f2fs/022

## Purpose

This is a regression test: 1. create foo & bar 2. write 8M data to foo 3. use inject.f2fs to inject i_nid[0] of foo w/ ino of bar 4. fpunch in foo w/ specified range

## Important APIs, Types, and Functions

This is a bash xfstests case in the `f2fs` suite. The harness entry and tags are `_begin_fstest auto quick rw`. No local shell functions are declared. Key xfstests/helper interfaces include `_require_scratch_nocheck` (requires scratch without pre-run fsck validation), `_scratch_unmount` (unmounts scratch to force persistence checks), `_scratch_mount` (mounts the scratch filesystem), `_scratch_mkfs` (formats the scratch filesystem). External or helper commands visible in the body include `stat`, `sync`, `touch`. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, `./common/attr`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_fixed_by_kernel_commit c18ecd99e0c7 \`; `_require_scratch_nocheck`; `_require_inject_f2fs_command node i_nid`; `foo_path=$SCRATCH_MNT/foo`; `bar_path=$SCRATCH_MNT/bar`; `_scratch_mkfs >> $seqres.full`; `_scratch_mount`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_inject_f2fs_command`, `_require_scratch_nocheck`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/attr` and with suite-specific filesystem features selected by the `f2fs` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.
