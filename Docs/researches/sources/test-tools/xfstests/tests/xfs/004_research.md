<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/004 -->
# sources/test-tools/xfstests/tests/xfs/004

## Purpose
`xfs_db freesp` accounting test. It populates a scratch filesystem, compares free-space totals against `df` plus reserved blocks, and verifies percentage columns sum to 100 after filtering volatile values.

## Important APIs, Types, And Functions
`_begin_fstest db auto quick` declares xfstests groups/tags: db, auto, quick. Imports `common/preamble`, `common/filter`. Local helpers: `_cleanup()`, `_populate_scratch()`. Feature gates/fix annotations include `_require_scratch`, `_require_no_large_scratch_dev`. External helper programs used include `xfs_db`, `$DF_PROG`, `$AWK_PROG`, `$XFS_IO_PROG`.

## Control Flow
The test is a XFS metadata inspection/editing test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 17: `_scratch_unmount`; line 18: `rm -f $tmp.*`; line 24: `_try_scratch_mkfs_xfs | tee -a $seqres.full | _filter_mkfs 2>$tmp.mkfs`; line 26: `_scratch_mount`; line 31: `dd if=/dev/zero of=$SCRATCH_MNT/foo count=200 bs=4096 >/dev/null 2>&1 &`; line 32: `dd if=/dev/zero of=$SCRATCH_MNT/goo count=400 bs=4096 >/dev/null 2>&1 &`; line 33: `dd if=/dev/zero of=$SCRATCH_MNT/moo count=800 bs=4096 >/dev/null 2>&1 &`; line 35: `_scratch_unmount # flush everything`; line 36: `_scratch_mount # and then remount`; line 53: `_scratch_xfs_db -r -c "freesp -s" >$tmp.xfs_db`.

## State And Persistence
State is kept in shell variables such as `ans`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; XFS tools and kernel interfaces exercised by the scenario, such as `xfs_db`, `xfs_io`, `xfs_repair`, `xfs_growfs`, `xfs_quota`, log sysfs/debugfs knobs, dump/restore tools, or repair filters.

## Risks And Test Signals
Risks: main risk is environmental: missing helper binaries, unsupported mount options, insufficient scratch space, or expected-output drift. Test signals: volatile paths, ids, device names, or tool output are filtered before golden comparison.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/004 -->
