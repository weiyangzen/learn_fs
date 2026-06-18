<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/020 -->
# sources/test-tools/xfstests/tests/xfs/020

## Purpose
Large sparse filesystem repair regression. It creates a 60TB file-backed XFS image and runs `xfs_repair -f -o ag_stride=32 -t 1`, checking for the historical progress-reporting segfault.

## Important APIs, Types, And Functions
`_begin_fstest auto repair` declares xfstests groups/tags: auto, repair. Imports `common/preamble`, `common/filter`. Local helpers: `_cleanup()`. Feature gates/fix annotations include `_require_test`, `_require_fs_space`. External helper programs used include `xfs_repair`, `xfs_io`, `$MKFS_PROG`, `$XFS_REPAIR_PROG`.

## Control Flow
The test is a XFS repair regression test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 19: `rm -f $tmp.*`; line 20: `rm -f $fsfile`; line 35: `rm -f $fsfile`; line 38: `truncate -s 60t $fsfile || _notrun "Cannot create 60T sparse file for test."`; line 39: `rm -f $fsfile`; line 41: `$MKFS_PROG -t xfs -d size=60t,file,name=$fsfile >/dev/null`; line 42: `$XFS_REPAIR_PROG -f -o ag_stride=32 -t 1 $fsfile >/dev/null 2>&1`.

## State And Persistence
State is kept in shell variables such as `fsfile`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; XFS tools and kernel interfaces exercised by the scenario, such as `xfs_db`, `xfs_io`, `xfs_repair`, `xfs_growfs`, `xfs_quota`, log sysfs/debugfs knobs, dump/restore tools, or repair filters.

## Risks And Test Signals
Risks: space/quota tests are sensitive to scratch capacity, mkfs geometry, and background reclaim. Test signals: quiet success usually prints `Silence is golden`; unsupported environments are skipped with `_notrun`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/020 -->
