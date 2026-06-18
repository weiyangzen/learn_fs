<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/002 -->
# sources/test-tools/xfstests/tests/xfs/002

## Purpose
Regression test for v4 secondary superblocks with junk in unused v5 CRC fields. It creates a non-CRC filesystem, writes garbage at the CRC offset in secondary superblocks, mounts, and expects `xfs_growfs` to tolerate the junk.

## Important APIs, Types, And Functions
`_begin_fstest auto quick growfs` declares xfstests groups/tags: auto, quick, growfs. Imports `common/preamble`, `common/filter`. Feature gates/fix annotations include `_require_scratch_nocheck`, `_require_no_large_scratch_dev`, `_require_xfs_nocrc`. External helper programs used include `$XFS_GROWFS_PROG`.

## Control Flow
The test is a XFS online growfs test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 27: `_scratch_mkfs_xfs -m crc=0 -d size=128m >> $seqres.full 2>&1`; line 32: `_scratch_xfs_db -x -c "sb 1" -c "type data" -c "write fill 0xff 224 4"`; line 33: `_scratch_xfs_db -x -c "sb 2" -c "type data" -c "write fill 0xff 224 4"`; line 35: `_scratch_mount`; line 38: `$XFS_GROWFS_PROG $SCRATCH_MNT >> $seqres.full 2>&1 || _fail "growfs failed"`.

## State And Persistence
State is mostly external to the script. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; XFS tools and kernel interfaces exercised by the scenario, such as `xfs_db`, `xfs_io`, `xfs_repair`, `xfs_growfs`, `xfs_quota`, log sysfs/debugfs knobs, dump/restore tools, or repair filters.

## Risks And Test Signals
Risks: main risk is environmental: missing helper binaries, unsupported mount options, insufficient scratch space, or expected-output drift. Test signals: explicit `_fail` calls mark invariant violations.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/002 -->
