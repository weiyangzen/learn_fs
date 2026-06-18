<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/005 -->
# sources/test-tools/xfstests/tests/xfs/005

## Purpose
Primary v5 superblock CRC mount-failure test. It creates a CRC-enabled XFS filesystem, directly corrupts the primary superblock CRC with `xfs_io`, and expects scratch mount to fail.

## Important APIs, Types, And Functions
`_begin_fstest auto quick` declares xfstests groups/tags: auto, quick. Imports `common/preamble`, `common/filter`. Feature gates/fix annotations include `_require_scratch_nocheck`. External helper programs used include `xfs_db`, `$XFS_IO_PROG`.

## Control Flow
The test is a XFS metadata inspection/editing test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 23: `_scratch_mkfs_xfs -m crc=1 >> $seqres.full 2>&1`; line 26: `$XFS_IO_PROG -c "pwrite 224 4" -c fsync $SCRATCH_DEV | _filter_xfs_io`; line 29: `_try_scratch_mount 2>&1 | _filter_error_mount`.

## State And Persistence
State is mostly external to the script. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; XFS tools and kernel interfaces exercised by the scenario, such as `xfs_db`, `xfs_io`, `xfs_repair`, `xfs_growfs`, `xfs_quota`, log sysfs/debugfs knobs, dump/restore tools, or repair filters.

## Risks And Test Signals
Risks: main risk is environmental: missing helper binaries, unsupported mount options, insufficient scratch space, or expected-output drift. Test signals: volatile paths, ids, device names, or tool output are filtered before golden comparison.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/005 -->
