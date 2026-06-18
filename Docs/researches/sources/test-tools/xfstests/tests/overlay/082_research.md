<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/082 -->
# sources/test-tools/xfstests/tests/overlay/082

## Purpose
Regression test for copying up a symlink that inherited the noatime inode attribute from a lower directory. It first proves the base filesystem exhibits symlink noatime inheritance, then moves the symlink through overlay to trigger symlink flag copy-up.

## Important APIs, Types, And Functions
`_begin_fstest auto quick copyup symlink atime` declares xfstests groups/tags: auto, quick, copyup, symlink, atime. Imports `common/preamble`. Feature gates/fix annotations include `_fixed_by_kernel_commit`, `_require_scratch`, `_require_chattr`. External helper programs used include `$CHATTR_PROG`, `$LSATTR_PROG`.

## Control Flow
The test is a overlayfs regression test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 23: `_scratch_mkfs`; line 27: `mkdir -p $lowerdir/testdir`; line 28: `$CHATTR_PROG +A $lowerdir/testdir >> $seqres.full 2>&1 ||`; line 41: `touch $lowerdir/testdir/foo`; line 42: `ln -sf foo $lowerdir/testdir/lnk`; line 43: `$LSATTR_PROG -l $lowerdir/testdir/foo >> $seqres.full`; line 56: `_scratch_mount`; line 60: `mv $SCRATCH_MNT/testdir/lnk $SCRATCH_MNT/`.

## State And Persistence
State is kept in shell variables such as `lowerdir`, `before`, `after`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: main risk is environmental: missing helper binaries, unsupported mount options, insufficient scratch space, or expected-output drift. Test signals: quiet success usually prints `Silence is golden`; unsupported environments are skipped with `_notrun`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/082 -->
