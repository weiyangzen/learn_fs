# sources/test-tools/xfstests/tests/generic/269

## Purpose

Run fsstress and ENOSPC hitters in parallel, check fs consistency at the end Disable all sync operations to get higher load. It is registered with `_begin_fstest auto rw prealloc ioctl enospc stress` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `269` plus `_begin_fstest auto rw prealloc ioctl enospc stress`. Imported libraries: `. ./common/preamble`, `. ./common/filter`. Capability gates: `_require_scratch`. Local functions: `_workout`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 15: `FSSTRESS_AVOID="$FSSTRESS_AVOID -ffsync=0 -fsync=0 -ffdatasync=0"`
- Line 21: `num_iterations=10`
- Line 22: `enospc_time=2`
- Line 23: `out=$SCRATCH_MNT/fsstress.$$`
- Line 24: `args=`_scale_fsstress_args -p128 -n999999999 -f setattr=1 -d $out``
- Line 51: `status=1`
- Line 54: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 18 `echo ""`, line 19 `echo "Run fsstress"`, line 20 `echo ""`, line 25 `echo "fsstress $args" >> $seqres.full`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 15: `FSSTRESS_AVOID="$FSSTRESS_AVOID -ffsync=0 -fsync=0 -ffdatasync=0"`
- Line 19: `echo "Run fsstress"`
- Line 23: `out=$SCRATCH_MNT/fsstress.$$`
- Line 24: `args=`_scale_fsstress_args -p128 -n999999999 -f setattr=1 -d $out``
- Line 25: `echo "fsstress $args" >> $seqres.full`
- Line 26: `_run_fsstress_bg $args`
- Line 27: `echo "Run dd writers in parallel"`
- Line 35: `echo "Killing fsstress process..." >> $seqres.full`
- Line 36: `_kill_fsstress`
- Line 39: `_require_scratch`
- Line 41: `_scratch_mkfs_sized $((512 * 1024 * 1024)) >> $seqres.full 2>&1`
- Line 42: `_scratch_mount`
- Line 45: `_scratch_unmount 2>/dev/null`
- Line 50: `echo "failed to umount"`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `rw`, `prealloc`, `ioctl`, `enospc`, `stress`, imports `. ./common/preamble`, `. ./common/filter`, and uses capability gates such as `_require_scratch`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.
- ENOSPC cases are deliberately capacity-sensitive and can expose allocator, reservation, or delayed-allocation leaks only when scratch sizing and reserved blocks match the scenario.
- Stress tests are randomized or high-iteration workloads, so seeds, scaling helpers, timeouts, and captured stderr are important for reproducibility.

## Test Signals

The pass signal is stress-tool exit status and captured logs. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
