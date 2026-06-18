# sources/test-tools/xfstests/tests/generic/005

## Purpose

Test symlinks & ELOOP Note: On Linux, ELOOP limit used to be 32 but changed to 8, and lately its become 5. Who knows what it might be next. What we are looking for here is: no panic due to blowing the stack; and that the ELOOP error code is returned at some point (the actual limit point is unimportant, just checking that we do hit it).

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest dir udf auto quick`. Important local functions are `_cleanup`, `_touch`. Key xfstests/helper interfaces include `_require_test` (requires the configured TEST_DIR filesystem). External or helper commands visible in the body include `grep`, `ln`, `rm`, `touch`. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_cleanup()`; `cd $TEST_DIR`; `rm -f symlink_{0,1,2,3,4}{0,1,2,3,4,5,6,7,8,9} symlink_self empty_file`; `_touch()`; `touch $@ 2>&1 | grep -q 'Too many levels of symbolic links'`; `if [ $? -eq 0 ]; then`; `echo "ELOOP returned.  Good."`.

## State and Persistence Behavior

The test mutates files under `TEST_DIR`. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_symlinks`, `_require_test`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: passes when required commands complete and the xfstests golden output matches. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.
