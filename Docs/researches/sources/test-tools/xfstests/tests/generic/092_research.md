# sources/test-tools/xfstests/tests/generic/092

## Purpose

fallocate/truncate tests with FALLOC_FL_KEEP_SIZE option. Verify if the disk space is released after truncating a file to i_size after writing to a portion of a preallocated range. This also verifies that truncat'ing up past i_size doesn't remove the preallocated space.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest auto quick prealloc fiemap`. No local shell functions are declared. Key xfstests/helper interfaces include `_require_xfs_io_command` (checks xfs_io subcommand support), `_filter_xfs_io` (normalizes xfs_io output), `_filter_fiemap` (normalizes fiemap output), `_require_test` (requires the configured TEST_DIR filesystem). External or helper commands visible in the body include `fiemap`. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, `./common/punch`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_require_test`; `_require_xfs_io_command "falloc"`; `_require_xfs_io_command "fiemap"`; `_require_congruent_file_oplen $TEST_DIR $((5 * 1048576))`; `_require_congruent_file_oplen $TEST_DIR $((7 * 1048576))`; `$XFS_IO_PROG -f -c "falloc -k 0 10M" -c "pwrite 0 5M" -c "truncate 5M"\`; `$TEST_DIR/testfile.$seq | _filter_xfs_io`.

## State and Persistence Behavior

The test mutates files under `TEST_DIR`. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_congruent_file_oplen`, `_require_test`, `_require_xfs_io_command`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter`, `./common/punch` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include extent layout assumptions can vary by filesystem feature and kernel version. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: passes when required commands complete and the xfstests golden output matches. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.
