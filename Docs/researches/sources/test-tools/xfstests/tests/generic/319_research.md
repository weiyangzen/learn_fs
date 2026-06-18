# sources/test-tools/xfstests/tests/generic/319

## Purpose

Regression test to make sure a directory inherits the default ACL from its parent directory. This test was motivated by an issue reported by a btrfs user. That issue is fixed and described by the following btrfs kernel patch: https://patchwork.kernel.org/patch/3046931/ success, all done. It is registered with `_begin_fstest acl auto quick perms` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `319` plus `_begin_fstest acl auto quick perms`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`. Capability gates: `_require_acls`, `_require_scratch`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 35: `status=0`

## Control Flow

The script runs linearly after the harness and requirement checks. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 22: `_require_scratch`
- Line 24: `_scratch_mkfs > /dev/null 2>&1`
- Line 25: `_scratch_mount`
- Line 27: `mkdir $SCRATCH_MNT/testdir`
- Line 29: `getfacl -n --absolute-names $SCRATCH_MNT/testdir | _filter_scratch`
- Line 31: `mkdir $SCRATCH_MNT/testdir/testsubdir`
- Line 32: `getfacl -n --absolute-names $SCRATCH_MNT/testdir/testsubdir | _filter_scratch`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `acl`, `auto`, `quick`, `perms`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`, and uses capability gates such as `_require_acls`, `_require_scratch`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.

## Test Signals

The pass signal is silence from the helper program and final `status=0`. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
