# sources/test-tools/xfstests/tests/generic/326

## Purpose

Ensure that quota charges us for reflinking a file and that we're not charged for directio copy on write. It is registered with `_begin_fstest auto quick clone fiemap` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `326` plus `_begin_fstest auto quick clone fiemap`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, `. ./common/quota`. Capability gates: `_require_scratch_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "fiemap"`, `_require_quota`, `_require_nobody`, `_require_odirect`, `_require_user`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 34: `testdir=$SCRATCH_MNT/test-$seq`
- Line 37: `sz=4194304`
- Line 68: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 26 `echo "Format and mount"`, line 38 `echo "Create the original files"`, line 49 `echo "Change file ownership"`, line 55 `echo "CoW one of the files"`. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 11: `_begin_fstest auto quick clone fiemap`
- Line 18: `_require_scratch_reflink`
- Line 20: `_require_xfs_io_command "fiemap"`
- Line 26: `echo "Format and mount"`
- Line 28: `export MOUNT_OPTIONS="-o usrquota,grpquota $MOUNT_OPTIONS"`
- Line 30: `_force_vfs_quota_testing $SCRATCH_MNT`
- Line 32: `quotaon $SCRATCH_MNT 2> /dev/null`
- Line 39: `$XFS_IO_PROG -f -c "pwrite -S 0x61 -b $sz 0 $sz" $testdir/file1 >> $seqres.full`
- Line 41: `_cp_reflink $testdir/file1 $testdir/file3 >> $seqres.full`
- Line 43: `chown nobody $testdir/urk`
- Line 45: `chown $qa_user $testdir/erk`
- Line 47: `_scratch_cycle_mount`
- Line 51: `chown $qa_user $testdir/file2`
- Line 65: `_report_quota_blocks $SCRATCH_MNT`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Cycle-mount calls force metadata and extent state through unmount/remount persistence before validation. Quota state is persistent filesystem metadata manipulated through `quotacheck`, `quotaon`, `setquota`, and `repquota` across user and group modes. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `clone`, `fiemap`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, `. ./common/quota`, and uses capability gates such as `_require_scratch_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "fiemap"`, `_require_quota`, `_require_nobody`, `_require_odirect`, `_require_user`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Quota tests depend on kernel quota mode, grace-period timing, and the qa user/group setup; stale quota files or unsupported VFS quota behavior can turn a real failure into a notrun or noisy output mismatch.
- Reflink coverage is sensitive to extent alignment, delayed allocation, unwritten extents, and page-size dependent block geometry, so comparisons against check files are the main correctness guard.
- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.
- Extent-map output is formatted and filtered, but the test still depends on stable extent flags, logical block addressing, and filesystem support for the ioctl under test.

## Test Signals

The pass signal is filtered extent-map output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
