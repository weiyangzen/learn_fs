# sources/test-tools/xfstests/tests/f2fs/010

## Purpose

This is a regression testcase to check whether we will handle database inode dirty status correctly: 1. create a regular file, and write data into the file 2. start transaction on the file (via F2FS_IOC_START_ATOMIC_WRITE) 3. write transaction data to the file 4. rename the file 5. commit and end the transaction (via F2FS_IOC_COMMIT_ATOMIC_WRITE) 6. drop caches in order to call f2fs_evict_inode() It expects kernel panic will gone after we apply commit 03511e936916 ("f2fs: fix inconsistent dirty state of atomic.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `f2fs` suite. The harness entry and tags are `_begin_fstest auto quick`. Important local functions are `_cleanup`. Key xfstests/helper interfaces include `_require_scratch` (requires a disposable scratch filesystem), `_require_command` (checks availability of an external command), `_scratch_mount` (mounts the scratch filesystem), `_scratch_mkfs` (formats the scratch filesystem). External or helper commands visible in the body include `f2fs_io`, `mv`, `rm`, `sync`. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_cleanup()`; `rm -r -f $tmp.*`; `_fixed_by_kernel_commit 03511e936916 \`; `_require_scratch`; `_require_command "$F2FS_IO_PROG" f2fs_io`; `_scratch_mkfs >> $seqres.full`; `_scratch_mount >> $seqres.full`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state, fio verification state for direct/atomic I/O. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_command`, `_require_scratch`. The test integrates with common xfstests libraries through `./common/preamble` and with suite-specific filesystem features selected by the `f2fs` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: prints `Silence is golden` after all checks pass; logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.
