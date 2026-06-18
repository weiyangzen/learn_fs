<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/003 -->
# sources/test-tools/xfstests/tests/xfs/003

## Purpose
Historical `xfs_db` stack/type command regression test. It runs several read-only command sequences (`pop`, `push`, `type`, `print`, `ring`) and fails on core files or unexpected nonzero status.

## Important APIs, Types, And Functions
`_begin_fstest db auto quick` declares xfstests groups/tags: db, auto, quick. Imports `common/preamble`, `common/filter`. Local helpers: `test_done()`. Feature gates/fix annotations include `_require_test`. External helper programs used include `xfs_db`.

## Control Flow
The test is a XFS metadata inspection/editing test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 27: `rm -f core`.

## State And Persistence
State is kept in shell variables such as `sts`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; XFS tools and kernel interfaces exercised by the scenario, such as `xfs_db`, `xfs_io`, `xfs_repair`, `xfs_growfs`, `xfs_quota`, log sysfs/debugfs knobs, dump/restore tools, or repair filters.

## Risks And Test Signals
Risks: main risk is environmental: missing helper binaries, unsupported mount options, insufficient scratch space, or expected-output drift. Test signals: exit status and golden stdout comparison.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/003 -->
