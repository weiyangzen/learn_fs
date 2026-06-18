# sources/test-tools/xfstests/tests/generic/320

## Purpose

heavy rm workload Regression test for commit: 9a3a5da xfs: check for stale inode before acquiring iflock on push Based on generic/273. It is registered with `_begin_fstest auto rw` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `320` plus `_begin_fstest auto rw`. Imported libraries: `. ./common/preamble`, `. ./common/filter`. Capability gates: `_require_scratch`. Local functions: `threads_set`, `file_create`, `worker`, `do_workload`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 23: `threads=100`
- Line 24: `count=2`
- Line 25: `fs_size=$((2 * 1024 * 1024 * 1024))`
- Line 26: `ORIGIN=$SCRATCH_MNT/origin`
- Line 30: `threads=$((LOAD_FACTOR * 100))`
- Line 33: `threads=200`
- Line 39: `i=0`
- Line 42: `disksize=$(($fs_size / 3))`

## Control Flow

The visible phases are driven by echo markers such as line 78 `echo "Silence is golden"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 21: `_require_scratch`
- Line 40: `mkdir $ORIGIN`
- Line 45: `$XFS_IO_PROG -f -c "pwrite 0 $((4096*count))" \`
- Line 55: `mkdir $SCRATCH_MNT/sub_$suffix`
- Line 58: `rm -rf $SCRATCH_MNT/sub_$suffix`
- Line 80: `_scratch_mkfs_sized $fs_size >>$seqres.full 2>&1`
- Line 81: `_scratch_mount >>$seqres.full 2>&1`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `rw`, imports `. ./common/preamble`, `. ./common/filter`, and uses capability gates such as `_require_scratch`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- The main risk is environment drift: missing helper binaries, unsupported filesystem operations, or output formatting changes can make the test skip or fail without indicating a filesystem regression.

## Test Signals

The pass signal is silence from the helper program and final `status=0`. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
