# sources/test-tools/xfstests/tests/generic/020

## Purpose

extended attributes

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest metadata attr udf auto quick`. Important local functions are `_attr`, `_attr_get_max`, `_attr_get_maxval_size`, `_attr_list`, `_filter`, `do_getfattr`, and others. Key xfstests/helper interfaces include `_require_attrs` (requires extended attribute support), `_require_test` (requires the configured TEST_DIR filesystem). External or helper commands visible in the body include `awk`, `dd`, `od`, `rm`, `sed`, `touch`. Significant variables include `BLOCK_SIZE`, `LEB_SIZE`, `OCTAL_SIZE`, `file`, `size`, `status`, `testfile`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, `./common/attr`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_filter()`; `sed "s#$TEST_DIR[^ :]*#<TESTFILE>#g;`; `_attr()`; `_filter $tmp.out`; `_filter $tmp.err 1>&2`; `_getfattr $* 2>$tmp.err >$tmp.out`; `_filter $tmp.out`.

## State and Persistence Behavior

The test mutates files under `TEST_DIR`. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_attrs`, `_require_btrfs_command`, `_require_test`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter`, `./common/attr` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.
