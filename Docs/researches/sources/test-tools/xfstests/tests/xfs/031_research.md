<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/031 -->
# sources/test-tools/xfstests/tests/xfs/031

## Purpose
Idempotent xfs_repair test. It creates protofile filesystems with shortform, block-form, and leaf-form root directories, runs repair multiple times, and checks later repair output matches the first pass.

## Important APIs, Types, And Functions
`_begin_fstest repair mkfs auto quick` declares xfstests groups/tags: repair, mkfs, auto, quick. Imports `common/preamble`, `common/repair`, `common/filter`. Local helpers: `_check_repair()`, `_create_proto()`. Feature gates/fix annotations include `_require_scratch`, `_require_no_large_scratch_dev`. External helper programs used include `xfs_repair`.

## Control Flow
The test is a XFS repair regression test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 17: `_check_repair()`; line 20: `_scratch_xfs_repair 2>&1 | _filter_repair | tee -a $seqres.full >$tmp.0`; line 24: `_scratch_xfs_repair 2>&1 | _filter_repair >$tmp.$i`; line 25: `diff $tmp.0 $tmp.$i >> $seqres.full`; line 82: `_scratch_mkfs_xfs -p $tmp.proto >$tmp.mkfs0 2>&1`; line 85: `_check_repair`; line 90: `_scratch_mkfs_xfs -p $tmp.proto | _filter_mkfs >/dev/null 2>&1`; line 91: `_check_repair`; line 96: `_scratch_mkfs_xfs -p $tmp.proto | _filter_mkfs >/dev/null 2>&1`; line 97: `_check_repair`.

## State And Persistence
State is kept in shell variables such as `total`, `count`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; XFS tools and kernel interfaces exercised by the scenario, such as `xfs_db`, `xfs_io`, `xfs_repair`, `xfs_growfs`, `xfs_quota`, log sysfs/debugfs knobs, dump/restore tools, or repair filters.

## Risks And Test Signals
Risks: main risk is environmental: missing helper binaries, unsupported mount options, insufficient scratch space, or expected-output drift. Test signals: content or output comparison is a primary failure signal; volatile paths, ids, device names, or tool output are filtered before golden comparison; unsupported environments are skipped with `_notrun`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/031 -->
