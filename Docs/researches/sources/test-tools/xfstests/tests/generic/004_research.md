# sources/test-tools/xfstests/tests/generic/004

## Purpose

Test O_TMPFILE opens, and linking them back into the namespace.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest auto quick`. Important local functions are `_cleanup`. Key xfstests/helper interfaces include `_require_xfs_io_command` (checks xfs_io subcommand support), `_filter_xfs_io` (normalizes xfs_io output), `_require_test` (requires the configured TEST_DIR filesystem). External or helper commands visible in the body include `rm`. Significant variables include `status`, `testfile`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_cleanup()`; `rm -f ${testfile}`; `_require_test`; `_require_xfs_io_command "-T"`; `_require_xfs_io_command "flink"`; `$XFS_IO_PROG -T \`; `rm ${testfile}`.

## State and Persistence Behavior

The test mutates temporary files under `$tmp.*` and harness result files. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_test`, `_require_xfs_io_command`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: passes when required commands complete and the xfstests golden output matches. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.
