# sources/test-tools/xfstests/tests/generic/028

## Purpose

The following commit introduced a race condition that causes getcwd(2) to return "/" instead of correct path 232d2d6 dcache: Translating dentry into pathname without taking rename_lock These commits fixed the bug ede4ceb prepend_path() needs to reinitialize dentry/vfsmount/mnt on restarts f650080 __dentry_path() fixes

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest auto quick`. No local shell functions are declared. Key xfstests/helper interfaces include `_require_test` (requires the configured TEST_DIR filesystem). No standalone external commands were extracted beyond shell builtins and xfstests helper calls.. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_require_test`; `echo "Silence is golden"`; `$here/src/t_getcwd $TEST_DIR`.

## State and Persistence Behavior

The test mutates files under `TEST_DIR`, mount/unmount state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_test`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include golden-output drift or unsupported prerequisite handling are the main maintenance risks. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: prints `Silence is golden` after all checks pass. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.
