<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/013 -->
# sources/test-tools/xfstests/tests/xfs/013

## Purpose
Free inode btree workload/stress test. It creates large hardlinked directory clones, randomly replaces files to generate sparse free inode chunks, runs fsstress concurrently, and lets finobt allocation/reuse problems surface as workload or cleanup failures.

## Important APIs, Types, And Functions
`_begin_fstest auto metadata stress` declares xfstests groups/tags: auto, metadata, stress. Imports `common/preamble`, `common/filter`. Local helpers: `filter_enospc()`, `_create()`, `_rand_replace()`, `_cleaner()`. Feature gates/fix annotations include `_require_scratch`, `_require_xfs_mkfs_finobt`, `_require_xfs_finobt`. External helper programs used include `fsstress`.

## Control Flow
The test is a XFS functional regression test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 28: `mkdir -p $dir`; line 44: `rm -f $dir/$file`; line 69: `rm -rf $dir/dir$i`; line 78: `_scratch_mkfs_xfs "-m crc=1,finobt=1 -d agcount=2" | \`; line 80: `_scratch_mount`; line 95: `_run_fsstress_bg -d $SCRATCH_MNT/fsstress -n 9999999 -p 2 -S t`; line 110: `cp -Rl $SCRATCH_MNT/dir$i $SCRATCH_MNT/dir$((i+1)) 2>&1 | \`; line 121: `rm -rf $SCRATCH_MNT/fsstress`; line 122: `rm -rf $SCRATCH_MNT/dir*`; line 125: `_scratch_unmount`.

## State And Persistence
State is kept in shell variables such as `dir`, `count`, `file`, `iters`, `mindirs`, `need`, `COUNT`, `LOOPS`, `MINDIRS`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; XFS tools and kernel interfaces exercised by the scenario, such as `xfs_db`, `xfs_io`, `xfs_repair`, `xfs_growfs`, `xfs_quota`, log sysfs/debugfs knobs, dump/restore tools, or repair filters.

## Risks And Test Signals
Risks: main risk is environmental: missing helper binaries, unsupported mount options, insufficient scratch space, or expected-output drift. Test signals: volatile paths, ids, device names, or tool output are filtered before golden comparison.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/013 -->
