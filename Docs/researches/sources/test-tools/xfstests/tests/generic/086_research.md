# sources/test-tools/xfstests/tests/generic/086

## Purpose

This test excercises the problem with unwritten and delayed extents in ext4 extent status tree where we might in some cases lose a block worth of data. Even though this was a ext4 specific problem the reproducer can be easily tun on any file system so let's do that just in case. This tests excercises the problem fixed in kernel with commit "ext4: Fix data corruption caused by unwritten and delayed extents"

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest auto prealloc preallocrw quick`. No local shell functions are declared. Key xfstests/helper interfaces include `_require_xfs_io_command` (checks xfs_io subcommand support), `_require_test` (requires the configured TEST_DIR filesystem). External or helper commands visible in the body include `rm`. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_require_test`; `_require_xfs_io_command "falloc"`; `rm -f $test_file`; `$XFS_IO_PROG -f -c "pwrite -S 0xaa 4096 2048" \`; `echo 3 > /proc/sys/vm/drop_caches`; `$XFS_IO_PROG -c "pwrite -S 0xdd 67584 2048" $test_file >> $seqres.full 2>&1`; `_hexdump $test_file`.

## State and Persistence Behavior

The test mutates temporary files under `$tmp.*` and harness result files. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_test`, `_require_xfs_io_command`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.
