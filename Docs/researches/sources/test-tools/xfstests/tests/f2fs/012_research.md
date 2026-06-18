# sources/test-tools/xfstests/tests/f2fs/012

## Purpose

This testcase checks whether linear lookup fallback works well or not as below: 1.create file w/ red heart as its filename 2.inject wrong hash code to the file 3.disable linear lookup, expect lookup failure 4.enable linear lookup, expect lookup succeed

## Important APIs, Types, and Functions

This is a bash xfstests case in the `f2fs` suite. The harness entry and tags are `_begin_fstest auto quick casefold`. Important local functions are `check_lookup`. Key xfstests/helper interfaces include `_require_scratch_nocheck` (requires scratch without pre-run fsck validation), `_try_scratch_mount` (attempts to mount scratch and lets the test decide skip/fail behavior), `_scratch_unmount` (unmounts scratch to force persistence checks), `_require_command` (checks availability of an external command), `_scratch_mount` (mounts the scratch filesystem). External or helper commands visible in the body include `f2fs_io`, `grep`, `mkdir`, `stat`, `touch`. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_fixed_by_kernel_commit 91b587ba79e1 \`; `_require_scratch_nocheck`; `_require_command "$F2FS_IO_PROG" f2fs_io`; `_require_inject_f2fs_command dent d_hash`; `_scratch_mkfs -O casefold -C utf8 >> $seqres.full`; `_try_scratch_mount "-o lookup_mode=auto" >> $seqres.full 2>&1`; `if [ $? == 0 ]; then`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state, device-mapper target state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_command`, `_require_inject_f2fs_command`, `_require_scratch_nocheck`. The test integrates with common xfstests libraries through `./common/preamble` and with suite-specific filesystem features selected by the `f2fs` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: prints `Silence is golden` after all checks pass; logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.
