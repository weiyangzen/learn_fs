# sources/test-tools/xfstests/tests/generic/225

## Purpose

Run the fiemap (file extent mapping) tester. It is registered with `_begin_fstest auto quick fiemap` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `225` plus `_begin_fstest auto quick fiemap`. Imported libraries: `. ./common/preamble`, `. ./common/filter`. Capability gates: `_require_scratch`, `_require_odirect`, `_require_xfs_io_command "fiemap"`, `_require_test_program "fiemap-tester"`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 22: `fiemapfile=$SCRATCH_MNT/$seq.fiemap`
- Line 23: `fiemaplog=$SCRATCH_MNT/$seq.log`
- Line 27: `seed=`date +%s``
- Line 38: `status=$?`
- Line 45: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 29 `echo "using seed $seed" >> $fiemaplog`, line 31 `echo "fiemap run without preallocation, with sync"`, line 42 `echo "fiemap run without preallocation or sync"`. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 10: `_begin_fstest auto quick fiemap`
- Line 15: `_require_scratch`
- Line 17: `_require_xfs_io_command "fiemap"`
- Line 19: `_scratch_mkfs > /dev/null 2>&1`
- Line 20: `_scratch_mount > /dev/null 2>&1`
- Line 22: `fiemapfile=$SCRATCH_MNT/$seq.fiemap`
- Line 23: `fiemaplog=$SCRATCH_MNT/$seq.log`
- Line 25: `_require_test_program "fiemap-tester"`
- Line 29: `echo "using seed $seed" >> $fiemaplog`
- Line 31: `echo "fiemap run without preallocation, with sync"`
- Line 32: `$here/src/fiemap-tester -q -S -s $seed -p 0 -r 200 $fiemapfile 2>&1 | tee -a $fiemaplog`
- Line 35: `if grep -q "Operation not supported" $fiemaplog; then`
- Line 42: `echo "fiemap run without preallocation or sync"`
- Line 43: `$here/src/fiemap-tester -q -s $seed -p 0 -r 200 $fiemapfile 2>&1 | tee -a $fiemaplog`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `fiemap`, imports `. ./common/preamble`, `. ./common/filter`, and uses capability gates such as `_require_scratch`, `_require_odirect`, `_require_xfs_io_command "fiemap"`, `_require_test_program "fiemap-tester"`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.
- Extent-map output is formatted and filtered, but the test still depends on stable extent flags, logical block addressing, and filesystem support for the ioctl under test.
- Several checks can intentionally call `_notrun`; this is expected for unsupported geometry or feature combinations and should be distinguished from a failing assertion.

## Test Signals

The pass signal is filtered extent-map output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
