# sources/test-tools/xfstests/tests/generic/223

## Purpose

File alignment tests. It is registered with `_begin_fstest auto quick prealloc` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `223` plus `_begin_fstest auto quick prealloc`. Imported libraries: `. ./common/preamble`, `. ./common/filter`. Capability gates: `_require_scratch`, `_require_xfs_io_command "falloc"`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 19: `BLOCKSIZE=4096`
- Line 70: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 25 `echo "=== mkfs with su $SUNIT_BLOCKS blocks x 4 ==="`, line 38 `echo "=== Testing size ${SIZE_MULT}*${SUNIT_K}k on ${SUNIT_K}k stripe ==="`, line 53 `echo "=== Testing size 1g falloc on ${SUNIT_K}k stripe ==="`, line 61 `echo "=== Testing size 1073745920 falloc on ${SUNIT_K}k stripe ==="`. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 16: `_require_scratch`
- Line 17: `_require_xfs_io_command "falloc"`
- Line 26: `_scratch_mkfs_geom $SUNIT_BYTES 4 $BLOCKSIZE >> $seqres.full 2>&1`
- Line 27: `_scratch_mount`
- Line 40: `$XFS_IO_PROG -f -c "falloc 0 $SIZE" \`
- Line 41: `$SCRATCH_MNT/file-$FILE-$SIZE-falloc \`
- Line 43: `$XFS_IO_PROG -f -c "pwrite -b $SIZE 0 $SIZE" \`
- Line 46: `$here/src/t_stripealign $SCRATCH_MNT/file-$FILE-$SIZE-falloc \`
- Line 47: `$SUNIT_BLOCKS | _filter_scratch`
- Line 49: `$SUNIT_BLOCKS | _filter_scratch`
- Line 53: `echo "=== Testing size 1g falloc on ${SUNIT_K}k stripe ==="`
- Line 54: `$XFS_IO_PROG -f -c "falloc 0 1g" \`
- Line 55: `$SCRATCH_MNT/file-1g-falloc >> $seqres.full 2>&1`
- Line 67: `_scratch_unmount`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `prealloc`, imports `. ./common/preamble`, `. ./common/filter`, and uses capability gates such as `_require_scratch`, `_require_xfs_io_command "falloc"`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- The main risk is environment drift: missing helper binaries, unsupported filesystem operations, or output formatting changes can make the test skip or fail without indicating a filesystem regression.

## Test Signals

The pass signal is silence from the helper program and final `status=0`. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
