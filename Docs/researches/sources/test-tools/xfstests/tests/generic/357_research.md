# sources/test-tools/xfstests/tests/generic/357

## Purpose

Check that we can't swapon a reflinked file For NFS, a reflink is just a CLONE operation, and after that point it's dealt with by the server. It is registered with `_begin_fstest auto quick clone swap` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `357` plus `_begin_fstest auto quick clone swap`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`. Capability gates: `_require_scratch_swapfile`, `_require_scratch_reflink`, `_require_cp_reflink`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 39: `testdir=$SCRATCH_MNT/test-$seq`
- Line 42: `blocks=160`
- Line 43: `blksz=65536`
- Line 57: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 35 `echo "Format and mount"`, line 45 `echo "Initialize file"`, line 51 `echo "Try to swapon"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 18: `rm -rf $tmp.*`
- Line 31: `_require_scratch_swapfile`
- Line 32: `_require_scratch_reflink`
- Line 33: `_require_cp_reflink`
- Line 35: `echo "Format and mount"`
- Line 36: `_scratch_mkfs > $seqres.full 2>&1`
- Line 37: `_scratch_mount >> $seqres.full 2>&1`
- Line 40: `mkdir $testdir`
- Line 47: `touch "$testdir/file2"`
- Line 49: `_cp_reflink $testdir/file1 $testdir/file2 2>&1 | _filter_scratch`
- Line 51: `echo "Try to swapon"`
- Line 52: `swapon $testdir/file1 2>&1 | _filter_scratch`
- Line 54: `swapoff $testdir/file1 >> $seqres.full 2>&1`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Swap activation state is external to normal file contents, so cleanup and negative-result filtering are important to avoid leaking an active swapfile. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `clone`, `swap`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, and uses capability gates such as `_require_scratch_swapfile`, `_require_scratch_reflink`, `_require_cp_reflink`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Reflink coverage is sensitive to extent alignment, delayed allocation, unwritten extents, and page-size dependent block geometry, so comparisons against check files are the main correctness guard.
- Swapfile tests depend on kernel restrictions around swap activation, holes, and shared extents; cleanup must avoid leaving swap enabled.

## Test Signals

The pass signal is silence from the helper program and final `status=0`. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
