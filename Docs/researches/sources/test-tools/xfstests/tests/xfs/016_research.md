<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/016 -->
# sources/test-tools/xfstests/tests/xfs/016

## Purpose
End-of-log overwrite regression test. It seeds the block after the internal log with a pattern, drives controlled log traffic to near wraparound, advances across the wrap, and repeatedly verifies the block after the log remains unchanged.

## Important APIs, Types, And Functions
`_begin_fstest rw auto quick` declares xfstests groups/tags: rw, auto, quick. Imports `common/preamble`, `common/filter`, `common/quota`. Local helpers: `_cleanup()`, `_block_filter()`, `_init()`, `_log_traffic()`, `_log_size()`, `_log_head()`, `_log_sunit()`, `_after_log()`, `_check_corrupt()`. Feature gates/fix annotations include `_require_scratch`. External helper programs used include `$here/src/devzero`, `$here/src/feature`, `$AWK_PROG`.

## Control Flow
The test is a XFS metadata inspection/editing test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 29: `rm -f $tmp.*`; line 31: `_scratch_unmount 2>/dev/null`; line 46: `_scratch_mkfs_xfs $force_opts >> $seqres.full 2>&1`; line 54: `$here/src/devzero -b 2048 -n $sz_mb -v 198 $SCRATCH_DEV # write 0xc6`; line 66: `_scratch_mkfs_xfs $force_opts >$tmp.mkfs0 2>&1`; line 75: `_qmount_option noquota`; line 93: `$here/src/feature -U $SCRATCH_DEV && \`; line 95: `$here/src/feature -G $SCRATCH_DEV && \`; line 97: `$here/src/feature -P $SCRATCH_DEV && \`; line 103: `touch $out`.

## State And Persistence
State is kept in shell variables such as `log_size_bb`, `log_size`, `force_opts`, `count`, `out`, `f`, `block`, `actual_log_size`, `head`, `lsunit`, `sample_size_ops`, `head1`, and 5 more. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; XFS tools and kernel interfaces exercised by the scenario, such as `xfs_db`, `xfs_io`, `xfs_repair`, `xfs_growfs`, `xfs_quota`, log sysfs/debugfs knobs, dump/restore tools, or repair filters.

## Risks And Test Signals
Risks: space/quota tests are sensitive to scratch capacity, mkfs geometry, and background reclaim. Test signals: volatile paths, ids, device names, or tool output are filtered before golden comparison; unsupported environments are skipped with `_notrun`; explicit `_fail` calls mark invariant violations.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/016 -->
