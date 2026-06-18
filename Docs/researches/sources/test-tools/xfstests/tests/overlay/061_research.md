<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/061 -->
# sources/test-tools/xfstests/tests/overlay/061

## Purpose
Demonstrates the known overlayfs mmap copy-up incoherency pattern using `xfs_io`: one read-only shared mapping and one writable shared mapping of the same file can observe different data until remount; the test documents and checks persistence after a mount cycle.

## Important APIs, Types, And Functions
`_begin_fstest posix copyup mmap` declares xfstests groups/tags: posix, copyup, mmap. Imports `common/preamble`, `common/filter`. Local helpers: `filter_xfs_io_mmap()`. Feature gates/fix annotations include `_require_scratch`, `_require_xfs_io_command`. External helper programs used include `$XFS_IO_PROG`.

## Control Flow
The test is a overlayfs regression test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 26: `_scratch_mkfs >>$seqres.full 2>&1`; line 30: `mkdir -p $lowerdir`; line 33: `_scratch_mount`; line 48: `$XFS_IO_PROG -r $SCRATCH_MNT/foo \`; line 59: `_scratch_cycle_mount`; line 63: `$XFS_IO_PROG -r $SCRATCH_MNT/foo \`.

## State And Persistence
State is kept in shell variables such as `lowerdir`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: main risk is environmental: missing helper binaries, unsupported mount options, insufficient scratch space, or expected-output drift. Test signals: volatile paths, ids, device names, or tool output are filtered before golden comparison.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/061 -->
