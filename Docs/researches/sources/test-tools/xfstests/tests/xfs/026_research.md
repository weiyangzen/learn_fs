<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/026 -->
# sources/test-tools/xfstests/tests/xfs/026

## Purpose
xfsdump/xfsrestore dump-file test instead of tape. It writes a dump file, restores it, and compares content.

## Important APIs, Types, And Functions
`_begin_fstest dump ioctl auto quick` declares xfstests groups/tags: dump, ioctl, auto, quick. Imports `common/preamble`, `common/dump`. Local helpers: `_cleanup()`. Feature gates/fix annotations include `_require_scratch`.

## Control Flow
The test is a XFS dump/restore utility test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 19: `rm -f $tmp.*`; line 26: `_scratch_mkfs_xfs >>$seqres.full`; line 27: `_scratch_mount`; line 30: `_do_dump_file`; line 31: `_do_restore_file`.

## State And Persistence
State is mostly external to the script. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; XFS tools and kernel interfaces exercised by the scenario, such as `xfs_db`, `xfs_io`, `xfs_repair`, `xfs_growfs`, `xfs_quota`, log sysfs/debugfs knobs, dump/restore tools, or repair filters.

## Risks And Test Signals
Risks: dump/restore tape tests depend on configured local or remote tape devices and inventory state. Test signals: content or output comparison is a primary failure signal.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/026 -->
