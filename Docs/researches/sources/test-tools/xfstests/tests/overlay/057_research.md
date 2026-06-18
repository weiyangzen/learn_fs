<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/057 -->
# sources/test-tools/xfstests/tests/overlay/057

## Purpose
Checks absolute redirect lookup through an opaque ancestor. The setup creates an opaque middle-layer parent and a child redirect to a lower layer; the overlay should still merge and list the redirected lower content before and after a mount cycle.

## Important APIs, Types, And Functions
`_begin_fstest auto quick redirect` declares xfstests groups/tags: auto, quick, redirect. Imports `common/preamble`, `common/filter`. Feature gates/fix annotations include `_require_scratch_nocheck`, `_require_scratch_overlay_features`. External helper programs used include `$UMOUNT_PROG`.

## Control Flow
The test is a overlayfs xattr/redirect/whiteout behavior test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 34: `_scratch_mkfs`; line 43: `mkdir -p $lowerdir $lowerdir2 $upperdir $workdir $workdir2`; line 44: `mkdir -p $lowerdir/origin`; line 45: `touch $lowerdir/origin/foo`; line 46: `_overlay_scratch_mount_dirs $lowerdir $lowerdir2 $workdir2 -o redirect_dir=on`; line 49: `mkdir $SCRATCH_MNT/pure`; line 50: `mv $SCRATCH_MNT/origin $SCRATCH_MNT/pure/redirect`; line 51: `$UMOUNT_PROG $SCRATCH_MNT`; line 52: `_overlay_scratch_mount_dirs $lowerdir2:$lowerdir $upperdir $workdir -o redirect_dir=on`; line 53: `mv $SCRATCH_MNT/pure/redirect $SCRATCH_MNT/redirect`.

## State And Persistence
State is kept in shell variables such as `lowerdir`, `lowerdir2`, `upperdir`, `workdir`, `workdir2`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: xattr and overlay metadata assertions depend on trusted/user xattr support and exact kernel on-disk semantics. Test signals: exit status and golden stdout comparison.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/057 -->
