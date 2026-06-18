<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/011 -->
# sources/test-tools/xfstests/tests/xfs/011

## Purpose
XFS log reservation leak test. It freezes the filesystem before and during fsstress and checks sysfs log grant head state against expected zero/minimum reservation ranges.

## Important APIs, Types, And Functions
`_begin_fstest auto freeze log metadata quick` declares xfstests groups/tags: auto, freeze, log, metadata, quick. Imports `common/preamble`, `common/filter`. Local helpers: `_cleanup()`, `_check_scratch_log_state_new()`, `_check_scratch_log_state_old()`, `_check_scratch_log_state()`. Feature gates/fix annotations include `_require_scratch`, `_require_freeze`, `_require_xfs_sysfs`. External helper programs used include `fsstress`, `xfs_freeze`.

## Control Flow
The test is a XFS log behavior test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 27: `xfs_freeze -u $SCRATCH_MNT 2>/dev/null`; line 30: `rm -f $tmp.*`; line 46: `_check_scratch_log_state_new()`; line 58: `_check_scratch_log_state_old()`; line 80: `_check_scratch_log_state()`; line 85: `xfs_freeze -f $SCRATCH_MNT`; line 88: `_check_scratch_log_state_new`; line 90: `_check_scratch_log_state_old`; line 93: `xfs_freeze -u $SCRATCH_MNT`; line 98: `_scratch_mkfs_xfs >> $seqres.full 2>&1`.

## State And Persistence
State is kept in shell variables such as `devname`, `attrprefix`, `space`, `log_head_cycle`, `log_head_bytes`, `cycle`, `bytes`, `iters`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; XFS tools and kernel interfaces exercised by the scenario, such as `xfs_db`, `xfs_io`, `xfs_repair`, `xfs_growfs`, `xfs_quota`, log sysfs/debugfs knobs, dump/restore tools, or repair filters.

## Risks And Test Signals
Risks: main risk is environmental: missing helper binaries, unsupported mount options, insufficient scratch space, or expected-output drift. Test signals: quiet success usually prints `Silence is golden`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/011 -->
