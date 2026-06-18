# sources/test-tools/xfstests/tests/generic/273

## Purpose

reservation test with heavy cp workload creator. It is registered with `_begin_fstest auto rw` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `273` plus `_begin_fstest auto rw`. Imported libraries: `. ./common/preamble`, `. ./common/filter`. Capability gates: `_require_scratch`. Local functions: `_cleanup`, `_threads_set`, `_file_create`, `_porter`, `_do_workload`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 14: `status=0 # success is the default!`
- Line 26: `threads=50`
- Line 27: `count=2`
- Line 31: `_cpu_num=`$here/src/feature -o``
- Line 32: `threads=$(($_cpu_num * 50))`
- Line 35: `threads=200`
- Line 41: `block_size=$1`
- Line 42: `_i=0`

## Control Flow

The visible phases are driven by echo markers such as line 46 `echo "mkdir origin err"`, line 84 `echo "mkdir sub_xxx err"`, line 92 `echo "_porter $_suffix not complete"`, line 121 `echo "------------------------------"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 20: `rm -rf $tmp.*`
- Line 21: `_scratch_unmount`
- Line 44: `if ! mkdir $SCRATCH_MNT/origin`
- Line 46: `echo "mkdir origin err"`
- Line 71: `dd if=/dev/zero of=file_$_i bs=$block_size count=$_count >/dev/null 2>&1`
- Line 82: `if ! mkdir $SCRATCH_MNT/sub_$_suffix`
- Line 84: `echo "mkdir sub_xxx err"`
- Line 95: `_scratch_sync`
- Line 119: `_require_scratch`
- Line 125: `_scratch_unmount 2>/dev/null`
- Line 126: `_scratch_mkfs_sized $((2 * 1024 * 1024 * 1024)) >>$seqres.full 2>&1`
- Line 127: `_scratch_mount`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `rw`, imports `. ./common/preamble`, `. ./common/filter`, and uses capability gates such as `_require_scratch`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.

## Test Signals

The pass signal is silence from the helper program and final `status=0`. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
