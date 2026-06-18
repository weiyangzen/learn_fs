<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/028 -->
# sources/test-tools/xfstests/tests/xfs/028

## Purpose
xfsinvutil inventory pruning test. It creates five dump sessions, records a midpoint date after the third, runs inventory utility pruning, and compares inventory before/after.

## Important APIs, Types, And Functions
`_begin_fstest dump ioctl auto quick` declares xfstests groups/tags: dump, ioctl, auto, quick. Imports `common/preamble`, `common/dump`. Local helpers: `_cleanup()`. Feature gates/fix annotations include `_require_scratch`.

## Control Flow
The test is a XFS dump/restore utility test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 19: `rm -f $tmp.*`; line 26: `_scratch_mkfs_xfs >>$seqres.full`; line 27: `_scratch_mount`; line 36: `_do_dump_file -L "session.$i"`; line 41: `rm $dump_file`; line 54: `_do_invutil -F`.

## State And Persistence
State is kept in shell variables such as `i`, `middate`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; XFS tools and kernel interfaces exercised by the scenario, such as `xfs_db`, `xfs_io`, `xfs_repair`, `xfs_growfs`, `xfs_quota`, log sysfs/debugfs knobs, dump/restore tools, or repair filters.

## Risks And Test Signals
Risks: main risk is environmental: missing helper binaries, unsupported mount options, insufficient scratch space, or expected-output drift. Test signals: exit status and golden stdout comparison.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/028 -->
