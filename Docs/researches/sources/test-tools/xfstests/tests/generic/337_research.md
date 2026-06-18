# sources/test-tools/xfstests/tests/generic/337

## Purpose

Test that the filesystem's implementation of the listxattrs system call lists all the xattrs an inode has Create our test file with a few xattrs. The first 3 xattrs have a name that when given as input to a crc32c function result in the same checksum. This made btrfs list only one of the xattrs through listxattrs system call (because it packs xattrs with the same name checksum into the same btree item) Now call getfattr with --dump, which calls the listxattrs system call It should list all the xattrs we have set before. It is registered with `_begin_fstest auto quick attr metadata` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `337` plus `_begin_fstest auto quick attr metadata`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`. Capability gates: `_require_scratch`, `_require_attrs`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 38: `status=0`

## Control Flow

The script runs linearly after the harness and requirement checks. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 17: `_require_scratch`
- Line 20: `_scratch_mkfs >>$seqres.full 2>&1`
- Line 21: `_scratch_mount`
- Line 27: `touch $SCRATCH_MNT/testfile`
- Line 36: `_getfattr --absolute-names --dump $SCRATCH_MNT/testfile | _filter_scratch`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `attr`, `metadata`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`, and uses capability gates such as `_require_scratch`, `_require_attrs`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Thin-provisioning tests depend on device-mapper target behavior, pool exhaustion semantics, and correct cleanup of temporary block devices.

## Test Signals

The pass signal is silence from the helper program and final `status=0`. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
