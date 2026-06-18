<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/032 -->
# sources/test-tools/xfstests/tests/xfs/032

## Purpose
xfs_copy coverage for sector/block size combinations. It formats each supported geometry, lightly populates with fsstress, copies with duplicate and normal modes, and validates copied images with `xfs_repair -n -f`.

## Important APIs, Types, And Functions
`_begin_fstest copy auto quick` declares xfstests groups/tags: copy, auto, quick. Imports `common/preamble`. Local helpers: `do_copy()`. Feature gates/fix annotations include `_require_scratch`, `_require_test_program`, `_require_xfs_copy`. External helper programs used include `xfs_copy`, `$here/src/feature`, `$XFS_COPY_PROG`, `xfs_repair`, `$XFS_REPAIR_PROG`.

## Control Flow
The test is a XFS repair regression test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 32: `$XFS_COPY_PROG $opts $SCRATCH_DEV $IMGFILE >> $seqres.full 2>&1 || \`; line 35: `$XFS_REPAIR_PROG -n -f $IMGFILE >> $seqres.full 2>&1 || \`; line 42: `_scratch_mkfs -s size=$SECTORSIZE -b size=$BLOCKSIZE -d size=1g >> $seqres.full 2>&1`; line 58: `_run_fsstress -n 100 -d $SCRATCH_MNT`; line 59: `_scratch_unmount`.

## State And Persistence
State is kept in shell variables such as `SECTORSIZE`, `PAGESIZE`, `IMGFILE`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; XFS tools and kernel interfaces exercised by the scenario, such as `xfs_db`, `xfs_io`, `xfs_repair`, `xfs_growfs`, `xfs_quota`, log sysfs/debugfs knobs, dump/restore tools, or repair filters.

## Risks And Test Signals
Risks: main risk is environmental: missing helper binaries, unsupported mount options, insufficient scratch space, or expected-output drift. Test signals: quiet success usually prints `Silence is golden`; explicit `_fail` calls mark invariant violations.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/032 -->
