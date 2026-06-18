<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/041 -->
# sources/test-tools/xfstests/tests/xfs/041

## Purpose
Online growfs QA test. It repeatedly fills the filesystem, grows from 32MB through partial/full allocation-group sizes, remounts, and verifies all generated files against a manifest after each grow.

## Important APIs, Types, And Functions
`_begin_fstest growfs ioctl auto` declares xfstests groups/tags: growfs, ioctl, auto. Imports `common/preamble`, `common/filter`. Local helpers: `_cleanup()`, `_fill()`. Feature gates/fix annotations include `_require_scratch`, `_require_no_large_scratch_dev`, `_require_xfs_scratch_non_zoned`. External helper programs used include `$here/src/fill2fs`, `xfs_growfs`, `$here/src/fill2fs_check`.

## Control Flow
The test is a XFS online growfs test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 19: `_scratch_unmount`; line 20: `rm -f $tmp.*`; line 29: `_scratch_unmount 2>/dev/null`; line 38: `_do_die_on_error=message_only`; line 41: `_scratch_mkfs_xfs -dsize=${agsize}m,agcount=1 2>&1 >/dev/null`; line 45: `_scratch_mount`.

## State And Persistence
State is kept in shell variables such as `_do_die_on_error`, `agsize`, `bsize`, `onemeginblocks`, `grow_size`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; XFS tools and kernel interfaces exercised by the scenario, such as `xfs_db`, `xfs_io`, `xfs_repair`, `xfs_growfs`, `xfs_quota`, log sysfs/debugfs knobs, dump/restore tools, or repair filters.

## Risks And Test Signals
Risks: main risk is environmental: missing helper binaries, unsupported mount options, insufficient scratch space, or expected-output drift. Test signals: volatile paths, ids, device names, or tool output are filtered before golden comparison.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/041 -->
