# sources/test-tools/xfstests/tests/f2fs/019

## Purpose

This is a regression test: 1. create a file 2. write file to create a direct node at special offset 3. use inject.f2fs to inject nid of direct node w/ ino of the inode 4. check whether f2fs kernel module will detect and report such corruption in the file

## Important APIs, Types, and Functions

This is a bash xfstests case in the `f2fs` suite. The harness entry and tags are `_begin_fstest auto quick rw`. No local shell functions are declared. Key xfstests/helper interfaces include `_require_scratch_nocheck` (requires scratch without pre-run fsck validation), `_scratch_unmount` (unmounts scratch to force persistence checks), `_scratch_mount` (mounts the scratch filesystem), `_scratch_mkfs` (formats the scratch filesystem). No standalone external commands were extracted beyond shell builtins and xfstests helper calls.. Significant variables include `status`, `testfile`.

## Control Flow

The script sources `./common/preamble`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_fixed_by_kernel_commit 77de19b6867f \`; `_require_scratch_nocheck`; `_require_inject_f2fs_command node addr`; `testfile=$SCRATCH_MNT/testfile`; `_scratch_mkfs >> $seqres.full`; `_scratch_mount`; `$XFS_IO_PROG -f -c "pwrite 3738M 1M" -c "fsync" $testfile >> $seqres.full`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_inject_f2fs_command`, `_require_scratch_nocheck`. The test integrates with common xfstests libraries through `./common/preamble` and with suite-specific filesystem features selected by the `f2fs` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.
