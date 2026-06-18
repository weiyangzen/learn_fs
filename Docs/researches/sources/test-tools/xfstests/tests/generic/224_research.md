# sources/test-tools/xfstests/tests/generic/224

## Purpose

Delayed allocation at ENOSPC test Derived from a test case from Lachlan McIlroy and improved to reliably trigger a BUG in xfs_get_blocks(). Despite this XFS focus, the test can to run on any filesystem to exercise ENOSPC behaviour make a 1GB filesystem set the reserved block pool to almost empty for XFS. It is registered with `_begin_fstest auto` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `224` plus `_begin_fstest auto`. Imported libraries: `. ./common/preamble`, `. ./common/filter`. Capability gates: `_require_scratch`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 39: `FILES=1000`
- Line 65: `status=$?`

## Control Flow

The visible phases are driven by echo markers such as line 58 `echo "*** Silence is golden ***"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 20: `rm -f $tmp.*`
- Line 21: `rm -f $SCRATCH_MNT/testfile.*`
- Line 28: `_require_scratch`
- Line 31: `_scratch_mkfs_sized `expr 1024 \* 1024 \* 1024` > $seqres.full 2>&1`
- Line 32: `_scratch_mount >> $seqres.full 2>&1`
- Line 36: `$XFS_IO_PROG -x -c "resblks 4" $SCRATCH_MNT >> $seqres.full 2>&1`
- Line 48: `$XFS_IO_PROG -f -c "truncate 10485760" $SCRATCH_MNT/testfile.$i`
- Line 49: `dd if=/dev/zero of=$SCRATCH_MNT/testfile.$i bs=4k conv=notrunc`
- Line 55: `dd of=/dev/null if=$SCRATCH_MNT/testfile.$i bs=512k iflag=direct > /dev/null 2>&1 &`
- Line 62: `_scratch_unmount`
- Line 63: `_check_dmesg _filter_aiodio_dmesg`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, imports `. ./common/preamble`, `. ./common/filter`, and uses capability gates such as `_require_scratch`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.
- ENOSPC cases are deliberately capacity-sensitive and can expose allocator, reservation, or delayed-allocation leaks only when scratch sizing and reserved blocks match the scenario.

## Test Signals

The pass signal is post-test dmesg scanning. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
