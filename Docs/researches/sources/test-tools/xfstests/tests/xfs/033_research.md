<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/033 -->
# sources/test-tools/xfstests/tests/xfs/033

## Purpose
XFS repair test for root, realtime bitmap, and realtime summary inode corruption. It selects CRC-specific output variants, disables quota side effects, corrupts target inodes with zero/all-one patterns, and filters known ID/nlink noise.

## Important APIs, Types, And Functions
`_begin_fstest repair auto quick` declares xfstests groups/tags: repair, auto, quick. Imports `common/preamble`, `common/filter`, `common/repair`, `common/quota`. Local helpers: `_cleanup()`, `_check_root_inos()`, `_filter_bad_ids()`, `filter_repair()`. Feature gates/fix annotations include `_require_scratch`, `_require_no_large_scratch_dev`. External helper programs used include `xfs_repair`, `$here/src/feature`.

## Control Flow
The test is a XFS repair regression test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 17: `_scratch_unmount 2>/dev/null`; line 18: `rm -f $tmp.*`; line 28: `_check_root_inos()`; line 31: `_check_repair $1 "inode $rootino"`; line 33: `_check_repair $1 "inode $rbmino"`; line 35: `_check_repair $1 "inode $rsumino"`; line 54: `_scratch_xfs_force_no_metadir`; line 57: `_scratch_mkfs_xfs | _filter_mkfs 2>$tmp.mkfs >/dev/null`; line 60: `_scratch_mkfs_xfs -isize=512 | _filter_mkfs 2>$tmp.mkfs >/dev/null`; line 75: `_qmount_option noquota`.

## State And Persistence
State is kept in shell variables such as `FEATURES`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; XFS tools and kernel interfaces exercised by the scenario, such as `xfs_db`, `xfs_io`, `xfs_repair`, `xfs_growfs`, `xfs_quota`, log sysfs/debugfs knobs, dump/restore tools, or repair filters.

## Risks And Test Signals
Risks: space/quota tests are sensitive to scratch capacity, mkfs geometry, and background reclaim. Test signals: volatile paths, ids, device names, or tool output are filtered before golden comparison; unsupported environments are skipped with `_notrun`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/033 -->
