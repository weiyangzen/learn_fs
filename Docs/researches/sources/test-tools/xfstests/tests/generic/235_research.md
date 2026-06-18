# sources/test-tools/xfstests/tests/generic/235

## Purpose

Test whether quota gets properly reenabled after remount read-write. It is registered with `_begin_fstest auto quota quick` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `235` plus `_begin_fstest auto quota quick`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/quota`. Capability gates: `_require_scratch`, `_require_quota`, `_require_user`. Local functions: `do_repquota`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 53: `status=0`

## Control Flow

Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 11: `_begin_fstest auto quota quick`
- Line 15: `. ./common/quota`
- Line 17: `_require_scratch`
- Line 18: `_require_quota`
- Line 21: `do_repquota()`
- Line 23: `repquota -u -g $SCRATCH_MNT | grep -v -E '^root|^$' | _filter_scratch`
- Line 27: `_scratch_mkfs >> $seqres.full 2>&1`
- Line 28: `_scratch_mount "-o usrquota,grpquota"`
- Line 29: `quotacheck -u -g $SCRATCH_MNT 2>/dev/null`
- Line 30: `quotaon $SCRATCH_MNT 2>/dev/null`
- Line 32: `touch $SCRATCH_MNT/testfile`
- Line 33: `chown $qa_user:$qa_user $SCRATCH_MNT/testfile`
- Line 35: `do_repquota`
- Line 51: `_scratch_unmount 2>/dev/null`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Quota state is persistent filesystem metadata manipulated through `quotacheck`, `quotaon`, `setquota`, and `repquota` across user and group modes. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quota`, `quick`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/quota`, and uses capability gates such as `_require_scratch`, `_require_quota`, `_require_user`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Quota tests depend on kernel quota mode, grace-period timing, and the qa user/group setup; stale quota files or unsupported VFS quota behavior can turn a real failure into a notrun or noisy output mismatch.

## Test Signals

The pass signal is quota usage/enforcement reports. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
