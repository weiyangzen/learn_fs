<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/059 -->
# sources/test-tools/xfstests/tests/overlay/059

## Purpose
Checks that duplicated upper origin references to the same lower file do not produce identical overlay `st_dev/st_ino` for distinct files. The failure signal is `diff` thinking diverged copies are the same.

## Important APIs, Types, And Functions
`_begin_fstest auto quick copyup` declares xfstests groups/tags: auto, quick, copyup. Imports `common/preamble`, `common/filter`. Local helpers: `create_origin_ref()`. Feature gates/fix annotations include `_require_scratch_nocheck`, `_require_scratch_feature`. External helper programs used include `$UMOUNT_PROG`.

## Control Flow
The test is a overlayfs metadata-only copy-up behavior test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 28: `touch $lowerdir/origin`; line 33: `_scratch_mount -o redirect_dir=on`; line 34: `mv $SCRATCH_MNT/origin $SCRATCH_MNT/$ref`; line 36: `$UMOUNT_PROG $SCRATCH_MNT`; line 46: `_scratch_mkfs`; line 54: `cp -a $upperdir/ref1 $upperdir/ref2`; line 61: `_scratch_mount -o redirect_dir=on`; line 65: `diff -q $SCRATCH_MNT/ref1 $SCRATCH_MNT/ref2 &>/dev/null && \`.

## State And Persistence
State is kept in shell variables such as `upperdir`, `lowerdir`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: xattr and overlay metadata assertions depend on trusted/user xattr support and exact kernel on-disk semantics. Test signals: quiet success usually prints `Silence is golden`; content or output comparison is a primary failure signal.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/059 -->
