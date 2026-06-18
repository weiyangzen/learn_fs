<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/001 -->
# sources/test-tools/xfstests/tests/xfs/001

## Purpose
Tests writable `xfs_db` handling of XFS BMBT extent fields. It creates a file with an extent, finds the inode BMBT prefix, writes zero, every bit value, and beyond-maximum values into extent fields, and also checks core generation writes including hex syntax.

## Important APIs, Types, And Functions
`_begin_fstest db auto quick` declares xfstests groups/tags: db, auto, quick. Imports `common/preamble`, `common/filter`. Local helpers: `_do_bit_test()`, `filter_output()`. Feature gates/fix annotations include `_require_scratch_nocheck`. External helper programs used include `xfs_db`.

## Control Flow
The test is a XFS metadata inspection/editing test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 14: `_do_bit_test()`; line 20: `_scratch_xfs_db -x -c "inode $FILE_INO" -c "write $field 0"`; line 23: `_scratch_xfs_db -x -c "inode $FILE_INO" \`; line 37: `_scratch_mkfs >/dev/null 2>&1`; line 38: `_scratch_mount`; line 46: `_scratch_unmount`; line 62: `_do_bit_test "${prefix}[0].extentflag" $BMBT_EXNTFLAG_BITLEN | filter_output`; line 63: `_do_bit_test "${prefix}[0].startoff" $BMBT_STARTOFF_BITLEN | filter_output`; line 64: `_do_bit_test "${prefix}[0].startblock" $BMBT_STARTBLOCK_BITLEN | filter_output`; line 65: `_do_bit_test "${prefix}[0].blockcount" $BMBT_BLOCKCOUNT_BITLEN | filter_output`.

## State And Persistence
State is kept in shell variables such as `field`, `bits`, `num`, `FILE_INO`, `BMBT_EXNTFLAG_BITLEN`, `BMBT_STARTOFF_BITLEN`, `BMBT_STARTBLOCK_BITLEN`, `BMBT_BLOCKCOUNT_BITLEN`, `prefix`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; XFS tools and kernel interfaces exercised by the scenario, such as `xfs_db`, `xfs_io`, `xfs_repair`, `xfs_growfs`, `xfs_quota`, log sysfs/debugfs knobs, dump/restore tools, or repair filters.

## Risks And Test Signals
Risks: main risk is environmental: missing helper binaries, unsupported mount options, insufficient scratch space, or expected-output drift. Test signals: volatile paths, ids, device names, or tool output are filtered before golden comparison; explicit `_fail` calls mark invariant violations.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/001 -->
