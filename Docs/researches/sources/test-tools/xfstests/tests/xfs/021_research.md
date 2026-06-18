<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/021 -->
# sources/test-tools/xfstests/tests/xfs/021

## Purpose
`xfs_db` attribute fork format test. It creates small and large extended attributes, records inode numbers, unmounts, and dumps shortform and remote/block attribute structures with filtering for CRC/parent variants.

## Important APIs, Types, And Functions
`_begin_fstest db attr auto quick` declares xfstests groups/tags: db, attr, auto, quick. Imports `common/preamble`, `common/filter`, `common/attr`. Local helpers: `_cleanup()`, `_attr()`, `do_getfattr()`. Feature gates/fix annotations include `_require_scratch`, `_require_attrs`. External helper programs used include `xfs_db`, `$AWK_PROG`.

## Control Flow
The test is a XFS extended-attribute/log-replay test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 21: `_scratch_unmount 2>/dev/null`; line 22: `rm -f $tmp.*`; line 59: `_scratch_unmount >/dev/null 2>&1`; line 62: `_scratch_mkfs_xfs >/dev/null`; line 65: `_scratch_mount`; line 77: `touch $testfile.1`; line 85: `touch $testfile.2`; line 109: `_scratch_unmount >>$seqres.full 2>&1 \`; line 114: `_scratch_xfs_db -r -c "inode $inum_1" -c "print a.sfattr" | \`; line 124: `_scratch_xfs_db -r -c "inode $inum_2" -c "a a.bmx[0].startblock" -c print \`.

## State And Persistence
State is kept in shell variables such as `exit`, `testfile`, `inum_1`, `inum_2`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; XFS tools and kernel interfaces exercised by the scenario, such as `xfs_db`, `xfs_io`, `xfs_repair`, `xfs_growfs`, `xfs_quota`, log sysfs/debugfs knobs, dump/restore tools, or repair filters.

## Risks And Test Signals
Risks: xattr and overlay metadata assertions depend on trusted/user xattr support and exact kernel on-disk semantics. Test signals: content or output comparison is a primary failure signal; explicit `_fail` calls mark invariant violations.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/021 -->
