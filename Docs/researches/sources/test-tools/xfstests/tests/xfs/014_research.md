<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/014 -->
# sources/test-tools/xfstests/tests/xfs/014

## Purpose
Speculative preallocation reclaim test for ENOSPC and EDQUOT. It creates files with post-EOF preallocations, forces low-space and quota-hard-limit conditions, and verifies new writers reclaim speculative preallocations instead of failing prematurely.

## Important APIs, Types, And Functions
`_begin_fstest auto enospc quick quota prealloc` declares xfstests groups/tags: auto, enospc, quick, quota, prealloc. Imports `common/preamble`, `common/filter`, `common/quota`. Local helpers: `_cleanup()`, `_spec_prealloc_file()`, `_consume_free_space()`, `_test_enospc()`, `_test_edquot()`. Feature gates/fix annotations include `_require_scratch`, `_require_xfs_io_command`, `_require_loop`, `_require_quota`, `_require_user`, `_require_group`. External helper programs used include `$XFS_IO_PROG`, `$DF_PROG`, `$AWK_PROG`, `$XFS_QUOTA_PROG`, `$MKFS_XFS_PROG`.

## Control Flow
The test is a XFS quota behavior test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 27: `_scratch_unmount 2>/dev/null`; line 28: `rm -f $tmp.*`; line 45: `rm -f $file`; line 51: `$XFS_IO_PROG -f -c "pwrite $i 32k" $file >> $seqres.full`; line 56: `$XFS_IO_PROG -c "pwrite 0 128m" $file >> $seqres.full`; line 80: `$XFS_IO_PROG -f -c "falloc 0 ${freesp}M" $dir/spc`; line 91: `rm -rf $dir/*`; line 103: `touch $dir/file.$i`; line 106: `$XFS_IO_PROG -f -c "pwrite 0 $write_size" $dir/file.$i \`; line 120: `rm -rf $dir/*`.

## State And Persistence
State is kept in shell variables such as `size`, `blocks`, `blocksize`, `prealloc_size`, `TOTAL_PREALLOC`, `dir`, `freesp`, `write_size`, `blks`, `orig_sp_time`, `LOOP_FILE`, `LOOP_MNT`, and 1 more. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; XFS tools and kernel interfaces exercised by the scenario, such as `xfs_db`, `xfs_io`, `xfs_repair`, `xfs_growfs`, `xfs_quota`, log sysfs/debugfs knobs, dump/restore tools, or repair filters.

## Risks And Test Signals
Risks: space/quota tests are sensitive to scratch capacity, mkfs geometry, and background reclaim. Test signals: quiet success usually prints `Silence is golden`; explicit `_fail` calls mark invariant violations.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/014 -->
