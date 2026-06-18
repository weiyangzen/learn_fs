# sources/test-tools/xfstests/tests/generic/260

## Purpose

Purpose of this test is to check FITRIM argument handling to make sure that the argument processing is right and that it does not overflow All these tests should return EINVAL since the start is beyond the end of. It is registered with `_begin_fstest auto quick trim` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `260` plus `_begin_fstest auto quick trim`. Imported libraries: `. ./common/preamble`, `. ./common/filter`. Capability gates: `_require_math`, `_require_scratch`, `_require_batched_discard $SCRATCH_MNT`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 13: `status=0`
- Line 14: `chpid=0`
- Line 15: `mypid=$$`
- Line 28: `fssize=$(_discard_max_offset_kb "$SCRATCH_MNT" "$SCRATCH_DEV")`
- Line 30: `beyond_eofs=$(_math "$fssize*2048")`
- Line 31: `max_64bit=$(_math "2^64 - 1")`
- Line 39: `out=$($FSTRIM_PROG -o $beyond_eofs $SCRATCH_MNT 2>&1)`
- Line 44: `out=$($FSTRIM_PROG -o $beyond_eofs -l1M $SCRATCH_MNT 2>&1)`

## Control Flow

The visible phases are driven by echo markers such as line 38 `echo "[+] Start beyond the end of fs (should fail)"`, line 41 `echo $out | _filter_scratch`, line 43 `echo "[+] Start beyond the end of fs with len set (should fail)"`, line 46 `echo $out | _filter_scratch`. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 22: `_require_scratch`
- Line 23: `_scratch_mkfs >/dev/null 2>&1`
- Line 24: `_scratch_mount`
- Line 41: `echo $out | _filter_scratch`
- Line 46: `echo $out | _filter_scratch`
- Line 51: `echo $out | _filter_scratch`
- Line 56: `echo $out | _filter_scratch`
- Line 58: `_scratch_unmount`
- Line 59: `_scratch_mkfs >/dev/null 2>&1`
- Line 60: `_scratch_mount`
- Line 78: `_scratch_unmount`
- Line 79: `_scratch_mkfs >/dev/null 2>&1`
- Line 80: `_scratch_mount`
- Line 171: `bytes=$($FSTRIM_PROG -v -l$len $SCRATCH_MNT | _filter_fstrim)`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `trim`, imports `. ./common/preamble`, `. ./common/filter`, and uses capability gates such as `_require_math`, `_require_scratch`, `_require_batched_discard $SCRATCH_MNT`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.

## Test Signals

The pass signal is silence from the helper program and final `status=0`. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
