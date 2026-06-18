# sources/test-tools/xfstests/tests/generic/231

## Purpose

Run fsx with quotas enabled and verify accounted quotas in the end Derived from test 127. It is registered with `_begin_fstest auto quota` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `231` plus `_begin_fstest auto quota`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/quota`. Capability gates: `_require_scratch`, `_require_quota`, `_require_user`. Local functions: `_fsx`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 17: `FSX_FILE_SIZE=64000000`
- Line 18: `FSX_ARGS="-q -l $FSX_FILE_SIZE -o 65536 -N 20000"`
- Line 22: `tasks=$1`
- Line 25: `SEED=$RANDOM`
- Line 55: `status=1`
- Line 61: `status=1`
- Line 67: `status=1`
- Line 73: `status=1`

## Control Flow

The visible phases are driven by echo markers such as line 23 `echo "=== FSX Standard Mode, Memory Mapping, $tasks Tasks ==="`, line 28 `echo "ltp/fsx $FSX_ARGS -S $SEED $SCRATCH_MNT/fsx_file$i" >>$seqres.full`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 11: `_begin_fstest auto quota`
- Line 15: `. ./common/quota`
- Line 20: `_fsx()`
- Line 28: `echo "ltp/fsx $FSX_ARGS -S $SEED $SCRATCH_MNT/fsx_file$i" >>$seqres.full`
- Line 29: `_su $qa_user -c "ltp/fsx $FSX_ARGS -S $SEED \`
- Line 30: `$FSX_AVOID $SCRATCH_MNT/fsx_file$i" >$tmp.output$i 2>&1 &`
- Line 39: `$XFS_IO_PROG -c 'fsync' $SCRATCH_MNT/fsx_file$i`
- Line 45: `_require_scratch`
- Line 46: `_require_quota`
- Line 49: `_scratch_mkfs >> $seqres.full 2>&1`
- Line 50: `_qmount_option "usrquota,grpquota"`
- Line 51: `_qmount`
- Line 53: `if ! _fsx 1; then`
- Line 91: `_scratch_unmount 2>/dev/null`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Quota state is persistent filesystem metadata manipulated through `quotacheck`, `quotaon`, `setquota`, and `repquota` across user and group modes. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quota`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/quota`, and uses capability gates such as `_require_scratch`, `_require_quota`, `_require_user`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Quota tests depend on kernel quota mode, grace-period timing, and the qa user/group setup; stale quota files or unsupported VFS quota behavior can turn a real failure into a notrun or noisy output mismatch.
- Stress tests are randomized or high-iteration workloads, so seeds, scaling helpers, timeouts, and captured stderr are important for reproducibility.

## Test Signals

The pass signal is quota usage/enforcement reports, stress-tool exit status and captured logs. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
