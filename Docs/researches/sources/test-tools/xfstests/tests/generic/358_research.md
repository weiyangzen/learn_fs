# sources/test-tools/xfstests/tests/generic/358

## Purpose

Share an extent amongst a bunch of files such that the refcount stays the same while the rate of change of the set of owners is steadily increasing. For example, an extent of 32 blocks is owned by 32 files. At block 1, change one of the owners. At block 2, change 2 of the owners, and so on. It is registered with `_begin_fstest auto quick clone` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `358` plus `_begin_fstest auto quick clone`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`. Capability gates: `_require_scratch_reflink`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 36: `testdir=$SCRATCH_MNT/test-$seq`
- Line 39: `blocks=64`
- Line 40: `blksz=65536`
- Line 59: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 32 `echo "Format and mount"`, line 43 `echo "Initialize file"`, line 46 `echo "Share the file n-ways"`, line 55 `echo "Check output"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 22: `rm -rf $tmp.*`
- Line 30: `_require_scratch_reflink`
- Line 32: `echo "Format and mount"`
- Line 33: `_scratch_mkfs > $seqres.full 2>&1`
- Line 34: `_scratch_mount >> $seqres.full 2>&1`
- Line 37: `mkdir $testdir`
- Line 44: `_pwrite_byte 0x61 0 $((blocks * blksz)) $testdir/file >> $seqres.full`
- Line 48: `_reflink_range $testdir/file 0 $testdir/file$nr.0 0 $((nr * blksz)) >> $seqres.full`
- Line 50: `_reflink_range $testdir/file $((nnr * blksz)) $testdir/file$nr.$nnr $((nnr * blksz)) $blksz >> $seqres.full`
- Line 53: `_scratch_cycle_mount`
- Line 56: `md5sum $testdir/file $testdir/file*.0 | _filter_scratch`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Cycle-mount calls force metadata and extent state through unmount/remount persistence before validation. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `clone`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, and uses capability gates such as `_require_scratch_reflink`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Reflink coverage is sensitive to extent alignment, delayed allocation, unwritten extents, and page-size dependent block geometry, so comparisons against check files are the main correctness guard.

## Test Signals

The pass signal is filtered `md5sum` output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
