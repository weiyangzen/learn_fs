<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/024 -->
# sources/test-tools/xfstests/tests/xfs/024

## Purpose
Incremental xfsdump test. It records bstat output, takes a full dump, appends more data, takes a level-1 dump, restores, and compares the final tree.

## Important APIs, Types, And Functions
`_begin_fstest dump ioctl tape` declares xfstests groups/tags: dump, ioctl, tape. Imports `common/preamble`, `common/dump`. Local helpers: `_cleanup()`. Feature gates/fix annotations include `_require_tape`, `_require_scratch`. External helper programs used include `$here/src/bstat`.

## Control Flow
The test is a XFS dump/restore utility test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 19: `rm -f $tmp.*`; line 28: `_scratch_mkfs_xfs >>$seqres.full`; line 29: `_scratch_mount`; line 33: `$here/src/bstat $SCRATCH_MNT >>$seqres.full`; line 35: `_do_dump`; line 37: `$here/src/bstat $SCRATCH_MNT >>$seqres.full`; line 39: `_do_dump -l 1`; line 40: `_do_restore`.

## State And Persistence
State is mostly external to the script. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; XFS tools and kernel interfaces exercised by the scenario, such as `xfs_db`, `xfs_io`, `xfs_repair`, `xfs_growfs`, `xfs_quota`, log sysfs/debugfs knobs, dump/restore tools, or repair filters.

## Risks And Test Signals
Risks: dump/restore tape tests depend on configured local or remote tape devices and inventory state. Test signals: content or output comparison is a primary failure signal.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/024 -->
