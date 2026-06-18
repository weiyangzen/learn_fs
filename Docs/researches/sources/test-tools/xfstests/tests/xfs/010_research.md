<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/010 -->
# sources/test-tools/xfstests/tests/xfs/010

## Purpose
Free inode btree repair test. It sparsely populates inodes to build finobt records, corrupts freecount and non-free records, repairs, then corrupts the finobt root in AGI and verifies repair regeneration.

## Important APIs, Types, And Functions
`_begin_fstest auto quick repair` declares xfstests groups/tags: auto, quick, repair. Imports `common/preamble`, `common/filter`, `common/repair`. Local helpers: `_cleanup()`, `_sparse_inode_populate()`, `_filter_dbval()`, `_corrupt_finobt_records()`, `_corrupt_finobt_root()`, `filter_finobt_repair()`. Feature gates/fix annotations include `_require_scratch`, `_require_xfs_mkfs_finobt`, `_require_xfs_finobt`. External helper programs used include `xfs_repair`, `$XFS_DB_PROG`.

## Control Flow
The test is a XFS repair regression test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 22: `_scratch_unmount 2>/dev/null`; line 23: `rm -f $tmp.*`; line 33: `touch $dir/$i`; line 42: `rm -f $dir/$i`; line 60: `$XFS_DB_PROG -x -c "fsb $free_root" -c "type finobt" \`; line 65: `$XFS_DB_PROG -x -c "fsb $free_root" -c "type finobt" \`; line 67: `$XFS_DB_PROG -x -c "fsb $free_root" -c "type finobt" \`; line 76: `$XFS_DB_PROG -x \`; line 88: `_scratch_mkfs_xfs "-m crc=1,finobt=1 -d agcount=2" | _filter_mkfs 2>$seqres.full`; line 91: `_scratch_mount`.

## State And Persistence
State is kept in shell variables such as `dir`, `count`, `dev`, `free_root`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; XFS tools and kernel interfaces exercised by the scenario, such as `xfs_db`, `xfs_io`, `xfs_repair`, `xfs_growfs`, `xfs_quota`, log sysfs/debugfs knobs, dump/restore tools, or repair filters.

## Risks And Test Signals
Risks: main risk is environmental: missing helper binaries, unsupported mount options, insufficient scratch space, or expected-output drift. Test signals: volatile paths, ids, device names, or tool output are filtered before golden comparison.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/010 -->
