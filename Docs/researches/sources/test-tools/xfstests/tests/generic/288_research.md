# sources/test-tools/xfstests/tests/generic/288

## Purpose

This check the FITRIM argument handling in the corner case where length is smaller than block size or zero. It is registered with `_begin_fstest auto quick ioctl trim` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `288` plus `_begin_fstest auto quick ioctl trim`. Imported libraries: `. ./common/preamble`, `. ./common/filter`. Capability gates: `_require_scratch`, `_require_batched_discard $SCRATCH_MNT`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 13: `status=0`
- Line 26: `out=$("$FSTRIM_PROG" -v -o0 -l0 $SCRATCH_MNT 2>&1)`
- Line 31: `out=$("$FSTRIM_PROG" -v -o0 -l100 $SCRATCH_MNT 2>&1)`

## Control Flow

The visible phases are driven by echo markers such as line 25 `echo "[+] Length is zero (should fail)"`, line 28 `echo $out | _filter_scratch`, line 30 `echo "[+] Length is smaller than block size (should fail)"`, line 33 `echo $out | _filter_scratch`. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 19: `_require_scratch`
- Line 21: `_scratch_mkfs >/dev/null 2>&1`
- Line 22: `_scratch_mount`
- Line 28: `echo $out | _filter_scratch`
- Line 33: `echo $out | _filter_scratch`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `ioctl`, `trim`, imports `. ./common/preamble`, `. ./common/filter`, and uses capability gates such as `_require_scratch`, `_require_batched_discard $SCRATCH_MNT`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- The main risk is environment drift: missing helper binaries, unsupported filesystem operations, or output formatting changes can make the test skip or fail without indicating a filesystem regression.

## Test Signals

The pass signal is silence from the helper program and final `status=0`. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
