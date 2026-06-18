# sources/test-tools/xfstests/tests/generic/024

## Purpose

Check renameat2 syscall with RENAME_NOREPLACE flag

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest auto quick`. No local shell functions are declared. Key xfstests/helper interfaces include `_require_test` (requires the configured TEST_DIR filesystem). External or helper commands visible in the body include `mkdir`. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, `./common/renameat2`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_require_test`; `_require_renameat2 noreplace`; `_require_symlinks`; `rename_dir=$TEST_DIR/$$`; `mkdir $rename_dir`; `_rename_tests $rename_dir -n`.

## State and Persistence Behavior

The test mutates files under `TEST_DIR`. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_renameat2`, `_require_symlinks`, `_require_test`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/renameat2` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include golden-output drift or unsupported prerequisite handling are the main maintenance risks. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: passes when required commands complete and the xfstests golden output matches. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.
