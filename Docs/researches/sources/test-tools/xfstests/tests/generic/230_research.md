# sources/test-tools/xfstests/tests/generic/230

## Purpose

Simple quota enforcement test. It is registered with `_begin_fstest auto quota quick` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `230` plus `_begin_fstest auto quota quick`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/quota`. Capability gates: `_require_scratch`, `_require_quota`, `_require_user`. Local functions: `test_files`, `test_enforcement`, `cleanup_files`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 96: `grace=2`
- Line 104: `BLOCK_SIZE=$(_get_file_block_size $SCRATCH_MNT)`
- Line 118: `type=u`
- Line 127: `type=g`
- Line 133: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 23 `echo; echo "### create files, setting up ownership (type=$type)"`, line 32 `echo "### some buffered IO (type=$type)"`, line 33 `echo "--- initiating IO..." >>$seqres.full`, line 35 `echo "Write 225 blocks..."`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 11: `_begin_fstest auto quota quick`
- Line 18: `_require_quota`
- Line 27: `chmod 777 $SCRATCH_MNT 2>/dev/null`
- Line 39: `repquota -$type $SCRATCH_MNT | grep -v "^root" >>$seqres.full 2>&1`
- Line 45: `repquota -$type $SCRATCH_MNT | grep -v "^root" >>$seqres.full 2>&1`
- Line 54: `_filter_xfs_io_error | tee -a $seqres.full`
- Line 61: `_filter_xfs_io_error | tee -a $seqres.full`
- Line 68: `_su $qa_user -c "touch $SCRATCH_MNT/file3 $SCRATCH_MNT/file4" \`
- Line 75: `setquota -$type $qa_user -T $grace $grace $SCRATCH_MNT 2>/dev/null`
- Line 79: `repquota -$type $SCRATCH_MNT | grep -v "^root" >>$seqres.full 2>&1`
- Line 85: `_filter_scratch | tee -a $seqres.full`
- Line 99: `_qmount_option 'defaults'`
- Line 103: `_force_vfs_quota_testing $SCRATCH_MNT`
- Line 131: `_scratch_unmount 2>/dev/null`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Quota state is persistent filesystem metadata manipulated through `quotacheck`, `quotaon`, `setquota`, and `repquota` across user and group modes. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quota`, `quick`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/quota`, and uses capability gates such as `_require_scratch`, `_require_quota`, `_require_user`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Quota tests depend on kernel quota mode, grace-period timing, and the qa user/group setup; stale quota files or unsupported VFS quota behavior can turn a real failure into a notrun or noisy output mismatch.

## Test Signals

The pass signal is quota usage/enforcement reports. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
