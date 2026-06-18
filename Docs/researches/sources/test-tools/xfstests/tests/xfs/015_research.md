<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/015 -->
# sources/test-tools/xfstests/tests/xfs/015

## Purpose
Online growfs inode-allocation test. Background workers exhaust inodes while the filesystem grows at least 4x; after growth, they must allocate inodes in the new space until the expanded inode pool is nearly full.

## Important APIs, Types, And Functions
`_begin_fstest auto enospc growfs` declares xfstests groups/tags: auto, enospc, growfs. Imports `common/preamble`, `common/filter`. Local helpers: `create_file()`. Feature gates/fix annotations include `_require_scratch`, `_require_xfs_scratch_non_zoned`, `_require_fs_space`. External helper programs used include `xfs_growfs`, `$XFS_GROWFS_PROG`, `$DF_PROG`.

## Control Flow
The test is a XFS online growfs test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 39: `_scratch_mkfs >/dev/null 2>&1`; line 40: `_scratch_mount`; line 49: `_scratch_unmount`; line 51: `_scratch_mkfs_sized $((96 * 1024 * 1024)) > $tmp.mkfs.raw`; line 55: `_scratch_mount`; line 62: `mkdir $SCRATCH_MNT/testdir_$i`; line 72: `$XFS_GROWFS_PROG -D $((dblocks * 4)) $SCRATCH_MNT >>$seqres.full`; line 75: `touch $tmp.growfs`; line 82: `$DF_PROG -i $SCRATCH_MNT >>$seqres.full`.

## State And Persistence
State is kept in shell variables such as `nr_worker`, `i`, `total_inode`, `used_inode`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; XFS tools and kernel interfaces exercised by the scenario, such as `xfs_db`, `xfs_io`, `xfs_repair`, `xfs_growfs`, `xfs_quota`, log sysfs/debugfs knobs, dump/restore tools, or repair filters.

## Risks And Test Signals
Risks: space/quota tests are sensitive to scratch capacity, mkfs geometry, and background reclaim. Test signals: volatile paths, ids, device names, or tool output are filtered before golden comparison.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/015 -->
