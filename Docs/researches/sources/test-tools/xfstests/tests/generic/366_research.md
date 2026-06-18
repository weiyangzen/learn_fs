# sources/test-tools/xfstests/tests/generic/366

## Purpose

Test if mixed direct read, direct write and buffered write on the same file will hang the filesystem This is exposed by an incoming btrfs feature, which allows a folio to be partial uptodate if the buffered write range is block aligned but not yet full folio aligned Such behavior makes btrfs to hang reliably under generic/095 This is the extracted minimal reproducer for 4k block size and 64K page size. It is registered with `_begin_fstest auto quick rw` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `366` plus `_begin_fstest auto quick rw`. Imported libraries: `. ./common/preamble`, `. ./common/filter`. Capability gates: `_require_scratch`, `_require_odirect 512 # see fio job1 config below`, `_require_aio`, `_require_fio $fio_config`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 29: `iterations=$((32 * LOAD_FACTOR))`
- Line 31: `fio_config=$tmp.fio`
- Line 32: `fio_out=$tmp.fio.out`
- Line 33: `blksz=`$here/src/min_dio_alignment $SCRATCH_MNT $SCRATCH_DEV``
- Line 36: `bs=8k`
- Line 37: `iodepth=1`
- Line 38: `randrepeat=1`
- Line 39: `size=256k`

## Control Flow

The visible phases are driven by echo markers such as line 98 `echo "=== fio $i/$iterations ===" >> $seqres.full`, line 102 `echo "Silence is golden"`. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 22: `_require_scratch`
- Line 23: `_require_odirect 512 # see fio job1 config below`
- Line 31: `fio_config=$tmp.fio`
- Line 32: `fio_out=$tmp.fio.out`
- Line 34: `cat >$fio_config <<EOF`
- Line 43: `ioengine=sync`
- Line 58: `_require_fio $fio_config`
- Line 61: `_scratch_mkfs >>$seqres.full 2>&1`
- Line 62: `_scratch_mount`
- Line 92: `$FIO_PROG $fio_config --ignore_error=,EIO --output=$fio_out`
- Line 94: `_scratch_unmount`
- Line 96: `_check_dmesg _filter_aiodio_dmesg`
- Line 98: `echo "=== fio $i/$iterations ===" >> $seqres.full`
- Line 99: `cat $fio_out >> $seqres.full`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `rw`, imports `. ./common/preamble`, `. ./common/filter`, and uses capability gates such as `_require_scratch`, `_require_odirect 512 # see fio job1 config below`, `_require_aio`, `_require_fio $fio_config`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.

## Test Signals

The pass signal is post-test dmesg scanning, stress-tool exit status and captured logs. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
