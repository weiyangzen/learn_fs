# sources/test-tools/xfstests/tests/generic/314

## Purpose

Test SGID inheritance on subdirectories Make dir owned by qa user, and an unrelated group: Make parent dir sgid Make subdir Subdir should have inherited sgid. It is registered with `_begin_fstest auto quick perms` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `314` plus `_begin_fstest auto quick perms`. Imported libraries: `. ./common/preamble`, `. ./common/filter`. Capability gates: `_require_test`, `_require_user`, `_require_chown`, `_require_sgid_inheritance`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 35: `status=0`

## Control Flow

The script runs linearly after the harness and requirement checks. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 15: `_require_test`
- Line 17: `_require_chown`
- Line 20: `rm -rf $TEST_DIR/$seq-dir`
- Line 23: `mkdir $TEST_DIR/$seq-dir`
- Line 24: `chown $qa_user:12345 $TEST_DIR/$seq-dir`
- Line 27: `chmod 2775 $TEST_DIR/$seq-dir`
- Line 30: `_su $qa_user -c "umask 022; mkdir $TEST_DIR/$seq-dir/subdir"`
- Line 33: `_ls_l $TEST_DIR/$seq-dir/ | grep -v total | _filter_test_dir | awk '{print $1,$NF}'`

## State and Persistence Behavior

Primary state lives under `$TEST_DIR`, making this a test-device workload rather than a scratch-device destructive test. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `perms`, imports `. ./common/preamble`, `. ./common/filter`, and uses capability gates such as `_require_test`, `_require_user`, `_require_chown`, `_require_sgid_inheritance`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.

## Test Signals

The pass signal is silence from the helper program and final `status=0`. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
