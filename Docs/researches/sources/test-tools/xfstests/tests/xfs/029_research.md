<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/029 -->
# sources/test-tools/xfstests/tests/xfs/029

## Purpose
mkfs log zeroing/logprint test. It creates a scratch XFS filesystem and filters `xfs_logprint` output to verify log zeroing information without volatile device/uuid values.

## Important APIs, Types, And Functions
`_begin_fstest mkfs logprint log auto quick` declares xfstests groups/tags: mkfs, logprint, log, auto, quick. Imports `common/preamble`, `common/filter`. Local helpers: `filter_logprint()`. Feature gates/fix annotations include `_require_scratch`.

## Control Flow
The test is a XFS log behavior test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 37: `_scratch_mkfs_xfs | _filter_mkfs 2>/dev/null`; line 40: `_scratch_xfs_logprint | filter_logprint`.

## State And Persistence
State is mostly external to the script. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; XFS tools and kernel interfaces exercised by the scenario, such as `xfs_db`, `xfs_io`, `xfs_repair`, `xfs_growfs`, `xfs_quota`, log sysfs/debugfs knobs, dump/restore tools, or repair filters.

## Risks And Test Signals
Risks: main risk is environmental: missing helper binaries, unsupported mount options, insufficient scratch space, or expected-output drift. Test signals: volatile paths, ids, device names, or tool output are filtered before golden comparison.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/029 -->
