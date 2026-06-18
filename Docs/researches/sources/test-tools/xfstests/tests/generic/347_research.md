# sources/test-tools/xfstests/tests/generic/347

## Purpose

Test very basic thin device usage, exhaustion, and growth. It is registered with `_begin_fstest auto quick rw thin` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `347` plus `_begin_fstest auto quick rw thin`. Imported libraries: `. ./common/preamble`, `. ./common/dmthin`. Capability gates: `_require_scratch_nocheck`, `_require_dm_target thin-pool`. Local functions: `_cleanup`, `_setup_thin`, `_workout`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 13: `BACKING_SIZE=$((500 * 1024 * 1024 / 512)) # 500M`
- Line 14: `VIRTUAL_SIZE=$((10 * $BACKING_SIZE)) # 5000M`
- Line 15: `GROW_SIZE=$((100 * 1024 * 1024 / 512)) # 100M`
- Line 62: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 60 `echo "=== completed"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 20: `_dmthin_cleanup`
- Line 21: `rm -f $tmp.*`
- Line 26: `_dmthin_init $BACKING_SIZE $VIRTUAL_SIZE`
- Line 27: `_dmthin_set_queue`
- Line 28: `_dmthin_mkfs`
- Line 29: `_dmthin_mount`
- Line 36: `$XFS_IO_PROG -f -c "pwrite -W 0 1M" $SCRATCH_MNT/file$I &>/dev/null`
- Line 39: `_scratch_sync`
- Line 41: `_dmthin_grow $GROW_SIZE`
- Line 45: `$XFS_IO_PROG -f -c "pwrite 0 1M" $SCRATCH_MNT/file$I &>/dev/null`
- Line 52: `_require_scratch_nocheck`
- Line 53: `_require_dm_target thin-pool`
- Line 57: `_dmthin_check_fs`
- Line 58: `_dmthin_cleanup`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `rw`, `thin`, imports `. ./common/preamble`, `. ./common/dmthin`, and uses capability gates such as `_require_scratch_nocheck`, `_require_dm_target thin-pool`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Thin-provisioning tests depend on device-mapper target behavior, pool exhaustion semantics, and correct cleanup of temporary block devices.

## Test Signals

The pass signal is silence from the helper program and final `status=0`. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
