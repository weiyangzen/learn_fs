# sources/test-tools/xfstests/tests/generic/072

## Purpose

Test truncate/collapse range race. And this test is also a regression test for kernel commit 23fffa9, fs: move falloc collapse range check into the filesystem methods If the race occurs, it will trigger a BUG_ON().

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest auto metadata stress collapse`. No local shell functions are declared. Key xfstests/helper interfaces include `_require_xfs_io_command` (checks xfs_io subcommand support), `_require_test` (requires the configured TEST_DIR filesystem). No standalone external commands were extracted beyond shell builtins and xfstests helper calls.. Significant variables include `INNER_LOOPS`, `NCPUS`, `OUTER_LOOPS`, `status`, `testfile`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_require_test`; `_require_xfs_io_command "fcollapse"`; `testfile=$TEST_DIR/testfile.$seq`; `if [ $NCPUS -gt 8 ]; then`; `for ((i=1; i <= OUTER_LOOPS; i++)); do`; `for ((i=1; i <= INNER_LOOPS; i++)); do`; `$XFS_IO_PROG -f -c 'truncate 100k' \`.

## State and Persistence Behavior

The test mutates files under `TEST_DIR`. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_test`, `_require_xfs_io_command`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: prints `Silence is golden` after all checks pass. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.
