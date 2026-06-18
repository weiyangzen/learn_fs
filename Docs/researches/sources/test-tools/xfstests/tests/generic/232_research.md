# sources/test-tools/xfstests/tests/generic/232

## Purpose

Run fsstress with quotas enabled and verify accounted quotas in the end Derived from test 231. It is registered with `_begin_fstest auto quota stress` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `232` plus `_begin_fstest auto quota stress`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/quota`. Capability gates: `_require_scratch`, `_require_quota`. Local functions: `_filter_num`, `_fsstress`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 31: `out=$SCRATCH_MNT/fsstress.$$`
- Line 32: `count=2000`
- Line 33: `args=`_scale_fsstress_args -d $out -n $count -p 7``
- Line 39: `status=1`
- Line 53: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 27 `echo ""`, line 28 `echo "Testing fsstress"`, line 29 `echo ""`, line 35 `echo "fsstress $args" >> $seqres.full`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 11: `_begin_fstest auto quota stress`
- Line 15: `. ./common/quota`
- Line 17: `_filter_num()`
- Line 25: `_fsstress()`
- Line 28: `echo "Testing fsstress"`
- Line 31: `out=$SCRATCH_MNT/fsstress.$$`
- Line 33: `args=`_scale_fsstress_args -d $out -n $count -p 7``
- Line 35: `echo "fsstress $args" >> $seqres.full`
- Line 36: `if ! _run_fsstress $args`
- Line 38: `echo " fsstress $args returned $?"`
- Line 43: `_require_scratch`
- Line 44: `_require_quota`
- Line 46: `_scratch_mkfs > $seqres.full 2>&1`
- Line 52: `_scratch_unmount`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Quota state is persistent filesystem metadata manipulated through `quotacheck`, `quotaon`, `setquota`, and `repquota` across user and group modes. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quota`, `stress`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/quota`, and uses capability gates such as `_require_scratch`, `_require_quota`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Quota tests depend on kernel quota mode, grace-period timing, and the qa user/group setup; stale quota files or unsupported VFS quota behavior can turn a real failure into a notrun or noisy output mismatch.
- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.
- Stress tests are randomized or high-iteration workloads, so seeds, scaling helpers, timeouts, and captured stderr are important for reproducibility.

## Test Signals

The pass signal is quota usage/enforcement reports, stress-tool exit status and captured logs. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
