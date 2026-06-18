# sources/test-tools/xfstests/tests/generic/247

## Purpose

Test for race between direct I/O and mmap Modify as appropriate this test leaves a 512MB file around if we abort the test during the run via a reboot or kernel panic. Hence just name the file $seq so that we can always clean up on the next run and not leave large stale files around on the testdir that can lead to ENOSPC issues over time. It is registered with `_begin_fstest auto quick rw mmap` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `247` plus `_begin_fstest auto quick rw mmap`. Imported libraries: `. ./common/preamble`, `. ./common/filter`. Capability gates: `_require_test`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 33: `testfile=$TEST_DIR/$seq`
- Line 36: `loops=500`
- Line 37: `iosize=1048576`
- Line 49: `start=`expr $loops - 1``
- Line 52: `offset=`expr $i \* $iosize``
- Line 66: `status=$?`

## Control Flow

The visible phases are driven by echo markers such as line 59 `echo "Silence is golden."`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 10: `_begin_fstest auto quick rw mmap`
- Line 18: `rm -f $tmp.* $testfile`
- Line 27: `_require_test`
- Line 34: `rm -f $testfile`
- Line 40: `dd if=/dev/zero of=$testfile bs=$iosize count=$loops &> /dev/null`
- Line 42: `_test_sync`
- Line 45: `dd if=/dev/zero of=$testfile oflag=direct bs=$iosize count=$loops conv=notrunc &> /dev/null &`
- Line 53: `$XFS_IO_PROG -f -c "mmap -w $offset $iosize" -c "mwrite $offset $iosize" $testfile`
- Line 63: `_test_unmount`
- Line 64: `_check_dmesg _filter_aiodio_dmesg`

## State and Persistence Behavior

Primary state lives under `$TEST_DIR`, making this a test-device workload rather than a scratch-device destructive test. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `rw`, `mmap`, imports `. ./common/preamble`, `. ./common/filter`, and uses capability gates such as `_require_test`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.
- mmap tests rely on page-cache writeback, timestamp granularity, and correct handling of dirty mappings across fsync, sync, or remount boundaries.
- ENOSPC cases are deliberately capacity-sensitive and can expose allocator, reservation, or delayed-allocation leaks only when scratch sizing and reserved blocks match the scenario.

## Test Signals

The pass signal is post-test dmesg scanning. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
