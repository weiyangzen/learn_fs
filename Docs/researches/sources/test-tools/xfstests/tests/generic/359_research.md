# sources/test-tools/xfstests/tests/generic/359

## Purpose

Make sure that the reference counting mechanism can handle the case where we share the first 1/4 of an extent with a file, share the last 1/4 of the extent with a second file, share the first half of the extent with N files, and share the second half of the extent with a different set of N files. The key point here is to test that we handle the case where a refcount extent record doesn't coincide exactly with the block mapping records. It is registered with `_begin_fstest auto quick clone` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `359` plus `_begin_fstest auto quick clone`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`. Capability gates: `_require_scratch_reflink`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 38: `testdir=$SCRATCH_MNT/test-$seq`
- Line 41: `blocks=64`
- Line 42: `blksz=65536`
- Line 44: `nr=4`
- Line 45: `halfway=$((blocks / 2 * blksz))`
- Line 46: `quarter=$((blocks / 4 * blksz))`
- Line 73: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 34 `echo "Format and mount"`, line 48 `echo "Initialize file"`, line 51 `echo "Share the first half of the extent"`, line 56 `echo "Share the last half of the extent"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 24: `rm -rf $tmp.*`
- Line 32: `_require_scratch_reflink`
- Line 34: `echo "Format and mount"`
- Line 35: `_scratch_mkfs > $seqres.full 2>&1`
- Line 36: `_scratch_mount >> $seqres.full 2>&1`
- Line 39: `mkdir $testdir`
- Line 49: `_pwrite_byte 0x61 0 $((blocks * blksz)) $testdir/file >> $seqres.full`
- Line 53: `_reflink_range $testdir/file 0 $testdir/file$nr.0 0 $halfway >> $seqres.full`
- Line 58: `_reflink_range $testdir/file $halfway $testdir/file$nr.1 0 $halfway >> $seqres.full`
- Line 62: `_reflink_range $testdir/file 0 $testdir/file.2 0 $quarter >> $seqres.full`
- Line 65: `_reflink_range $testdir/file $((quarter * 3)) $testdir/file.3 0 $quarter >> $seqres.full`
- Line 67: `_scratch_cycle_mount`
- Line 70: `md5sum $testdir/file $testdir/file* | _filter_scratch`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Cycle-mount calls force metadata and extent state through unmount/remount persistence before validation. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `clone`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, and uses capability gates such as `_require_scratch_reflink`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Reflink coverage is sensitive to extent alignment, delayed allocation, unwritten extents, and page-size dependent block geometry, so comparisons against check files are the main correctness guard.

## Test Signals

The pass signal is filtered `md5sum` output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
