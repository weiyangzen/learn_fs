# sources/test-tools/xfstests/tests/f2fs/023

## Purpose

This testcase tries to inject fault into inode.i_inline_xattr_size, and check whether sanity check of f2fs can handle fault correctly.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `f2fs` suite. The harness entry and tags are `_begin_fstest auto quick rw attr`. No local shell functions are declared. Key xfstests/helper interfaces include `_require_scratch_nocheck` (requires scratch without pre-run fsck validation), `_scratch_unmount` (unmounts scratch to force persistence checks), `_filter_scratch` (normalizes scratch paths in stdout), `_scratch_mount` (mounts the scratch filesystem), `_require_attrs` (requires extended attribute support). External or helper commands visible in the body include `grep`, `touch`. Significant variables include `status`, `testfile`.

## Control Flow

The script sources `./common/preamble`, `./common/attr`, `./common/filter`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_fixed_by_kernel_commit 5c1768b67250 \`; `_require_attrs`; `_require_scratch_nocheck`; `_require_inject_f2fs_command node i_inline`; `_require_inject_f2fs_command node i_inline_xattr_size`; `testfile=$SCRATCH_MNT/testfile`; `_scratch_mkfs "-O extra_attr,flexible_inline_xattr" >> $seqres.full || _fail "mkfs failed"`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_attrs`, `_require_inject_f2fs_command`, `_require_scratch_nocheck`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/attr`, `./common/filter` and with suite-specific filesystem features selected by the `f2fs` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.
