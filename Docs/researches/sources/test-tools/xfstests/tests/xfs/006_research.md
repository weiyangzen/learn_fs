<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/006 -->
# sources/test-tools/xfstests/tests/xfs/006

## Purpose
XFS fail-at-unmount error-handling test. It uses dm-error, resets XFS sysfs error handling, runs metadata fsstress, loads an error table with lockfs, and verifies unmount does not retry forever and the filesystem can replay after restoring the working table.

## Important APIs, Types, And Functions
`_begin_fstest auto quick mount eio` declares xfstests groups/tags: auto, quick, mount, eio. Imports `common/preamble`, `common/filter`, `common/dmerror`. Local helpers: `_cleanup()`. Feature gates/fix annotations include `_require_scratch`, `_require_dm_target`, `_require_fs_sysfs`. External helper programs used include `fsstress`.

## Control Flow
The test is a XFS functional regression test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 17: `_dmerror_cleanup`; line 19: `rm -f $tmp.*`; line 30: `_scratch_mkfs > $seqres.full 2>&1`; line 31: `_dmerror_init`; line 32: `_dmerror_mount`; line 49: `_run_fsstress -z -n 5000 -p 10 \`; line 66: `_dmerror_load_error_table lockfs`; line 67: `_dmerror_unmount`; line 71: `_dmerror_load_working_table`; line 72: `_dmerror_mount`.

## State And Persistence
State is kept in shell variables such as `attr`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; XFS tools and kernel interfaces exercised by the scenario, such as `xfs_db`, `xfs_io`, `xfs_repair`, `xfs_growfs`, `xfs_quota`, log sysfs/debugfs knobs, dump/restore tools, or repair filters.

## Risks And Test Signals
Risks: uses disruptive kernel/storage state such as cache dropping, shutdown, dm-error, error injection, or crash/hang triggers. Test signals: explicit `_fail` calls mark invariant violations.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/006 -->
