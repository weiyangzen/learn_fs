# sources/test-tools/xfstests/tests/generic/270

## Purpose

Run fsstress and ENOSPC hitters in parallel, check quota and fs consistency at the end Disable all sync operations to get higher load. It is registered with `_begin_fstest auto quota rw prealloc ioctl enospc stress` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `270` plus `_begin_fstest auto quota rw prealloc ioctl enospc stress`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/quota`, `. ./common/attr`. Capability gates: `_require_quota`, `_require_user`, `_require_scratch`, `_require_command "$SETCAP_PROG" setcap`, `_require_attrs security`. Local functions: `_workout`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 19: `FSSTRESS_AVOID="$FSSTRESS_AVOID -ffsync=0 -fsync=0 -ffdatasync=0"`
- Line 25: `num_iterations=10`
- Line 26: `enospc_time=2`
- Line 27: `out=$SCRATCH_MNT/fsstress.$$`
- Line 28: `args=`_scale_fsstress_args -p128 -n999999999 -f setattr=1 $FSSTRESS_AVOID -d $out``
- Line 41: `_FSSTRESS_PID=$!`
- Line 48: `of=$SCRATCH_MNT/SPACE_CONSUMER bs=1M " \`
- Line 75: `status=1`

## Control Flow

The visible phases are driven by echo markers such as line 22 `echo ""`, line 23 `echo "Run fsstress"`, line 24 `echo ""`, line 29 `echo "fsstress $args" >> $seqres.full`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 11: `_begin_fstest auto quota rw prealloc ioctl enospc stress`
- Line 15: `. ./common/quota`
- Line 19: `FSSTRESS_AVOID="$FSSTRESS_AVOID -ffsync=0 -fsync=0 -ffdatasync=0"`
- Line 23: `echo "Run fsstress"`
- Line 27: `out=$SCRATCH_MNT/fsstress.$$`
- Line 28: `args=`_scale_fsstress_args -p128 -n999999999 -f setattr=1 $FSSTRESS_AVOID -d $out``
- Line 29: `echo "fsstress $args" >> $seqres.full`
- Line 31: `cp $FSSTRESS_PROG $tmp.fsstress.bin`
- Line 32: `$SETCAP_PROG cap_chown=epi $tmp.fsstress.bin`
- Line 39: `ulimit -l unlimited`
- Line 40: `_su $qa_user -c "$tmp.fsstress.bin $args" > /dev/null 2>&1 &`
- Line 43: `echo "Run dd writers in parallel"`
- Line 47: `_su $qa_user -c "dd if=/dev/zero \`
- Line 81: `echo "failed to umount"`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Quota state is persistent filesystem metadata manipulated through `quotacheck`, `quotaon`, `setquota`, and `repquota` across user and group modes. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quota`, `rw`, `prealloc`, `ioctl`, `enospc`, `stress`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/quota`, `. ./common/attr`, and uses capability gates such as `_require_quota`, `_require_user`, `_require_scratch`, `_require_command "$SETCAP_PROG" setcap`, `_require_attrs security`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Quota tests depend on kernel quota mode, grace-period timing, and the qa user/group setup; stale quota files or unsupported VFS quota behavior can turn a real failure into a notrun or noisy output mismatch.
- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.
- ENOSPC cases are deliberately capacity-sensitive and can expose allocator, reservation, or delayed-allocation leaks only when scratch sizing and reserved blocks match the scenario.
- Stress tests are randomized or high-iteration workloads, so seeds, scaling helpers, timeouts, and captured stderr are important for reproducibility.

## Test Signals

The pass signal is quota usage/enforcement reports, stress-tool exit status and captured logs. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
