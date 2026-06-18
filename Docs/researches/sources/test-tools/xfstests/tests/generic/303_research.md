# sources/test-tools/xfstests/tests/generic/303

## Purpose

Check that high-offset reflinks work. It is registered with `_begin_fstest auto quick clone` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `303` plus `_begin_fstest auto quick clone`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`, `. ./common/reflink`. Capability gates: `_require_test_reflink`, `_require_cp_reflink`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 28: `testdir=$TEST_DIR/test-$seq`
- Line 32: `bigoff=9223372036854775806`
- Line 33: `len=9223372036854775807`
- Line 34: `bigoff_64k=9223372036854710272 # bigoff rounded down to 64k`
- Line 73: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 27 `echo "Format and mount"`, line 31 `echo "Create the original files"`, line 40 `echo "Reflink large single byte file"`, line 43 `echo "Reflink large empty file"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 16: `rm -rf $tmp.* $testdir`
- Line 24: `_require_test_reflink`
- Line 25: `_require_cp_reflink`
- Line 27: `echo "Format and mount"`
- Line 29: `mkdir $testdir`
- Line 35: `$XFS_IO_PROG -f -c "truncate $len" $testdir/file0 >> $seqres.full`
- Line 36: `test -s $testdir/file0 || _notrun "High offset ftruncate failed"`
- Line 37: `_pwrite_byte 0x61 $bigoff 1 $testdir/file1 >> $seqres.full`
- Line 38: `_pwrite_byte 0x61 1048575 1 $testdir/file2 >> $seqres.full`
- Line 41: `_cp_reflink $testdir/file1 $testdir/file3 >> $seqres.full`
- Line 44: `_cp_reflink $testdir/file0 $testdir/file4 >> $seqres.full`
- Line 47: `_reflink_range $testdir/file1 0 $testdir/file5 4611686018427322368 $len >> $seqres.full`
- Line 50: `_reflink_range $testdir/file1 $bigoff_64k $testdir/file6 1048576 65535 >> $seqres.full`
- Line 69: `$XFS_IO_PROG -c "pread -v -q 1114110 1" $testdir/file6`

## State and Persistence Behavior

Primary state lives under `$TEST_DIR`, making this a test-device workload rather than a scratch-device destructive test. Cycle-mount calls force metadata and extent state through unmount/remount persistence before validation. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `clone`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`, `. ./common/reflink`, and uses capability gates such as `_require_test_reflink`, `_require_cp_reflink`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Reflink coverage is sensitive to extent alignment, delayed allocation, unwritten extents, and page-size dependent block geometry, so comparisons against check files are the main correctness guard.
- Several checks can intentionally call `_notrun`; this is expected for unsupported geometry or feature combinations and should be distinguished from a failing assertion.

## Test Signals

The pass signal is silence from the helper program and final `status=0`. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
