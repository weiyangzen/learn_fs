# sources/test-tools/xfstests/tests/generic/088

## Purpose

test out CAP_DAC_OVERRIDE and CAP_DAC_SEARCH code in xfs_iaccess(ip,mode,cr)

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest perms auto quick`. Important local functions are `_filter`. Key xfstests/helper interfaces include `_require_test` (requires the configured TEST_DIR filesystem). External or helper commands visible in the body include `sed`. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_filter()`; `_filter_test_dir | sed -e '/----------/d'`; `_require_test`; `_require_chown`; `path=$TEST_DIR/t_access`.

## State and Persistence Behavior

The test mutates files under `TEST_DIR`. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_chown`, `_require_test`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include golden-output drift or unsupported prerequisite handling are the main maintenance risks. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.
