<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/065 -->
# sources/test-tools/xfstests/tests/overlay/065

## Purpose
Mount and lookup regression test for overlapping overlay layers. It checks same/overlapping upper, work, and lower directories, duplicate lower layers, overlap with another mounted overlay upper/work dir with index on/off, and post-mount overlap detection.

## Important APIs, Types, And Functions
`_begin_fstest auto quick mount` declares xfstests groups/tags: auto, quick, mount. Imports `common/preamble`, `common/filter`. Local helpers: `_cleanup()`. Feature gates/fix annotations include `_fixed_in_kernel_version`, `_fixed_by_kernel_commit`, `_require_scratch_nocheck`, `_require_scratch_feature`. External helper programs used include `$UMOUNT_PROG`.

## Control Flow
The test is a overlayfs mount option validation test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 32: `rm -f $tmp.*`; line 33: `$UMOUNT_PROG $mnt2 2>/dev/null`; line 49: `_scratch_mkfs`; line 60: `mkdir -p $lowerdir/lower $upperdir $workdir`; line 64: `_overlay_scratch_mount_dirs $upperdir $upperdir $workdir \`; line 66: `$UMOUNT_PROG $SCRATCH_MNT 2>/dev/null`; line 70: `rm -rf $upperdir $workdir`; line 71: `mkdir $upperdir $workdir`; line 76: `_overlay_scratch_mount_dirs $workdir $upperdir $workdir \`; line 78: `$UMOUNT_PROG $SCRATCH_MNT 2>/dev/null`.

## State And Persistence
State is kept in shell variables such as `basedir`, `lowerdir`, `upperdir`, `workdir`, `upperdir2`, `workdir2`, `mnt2`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: main risk is environmental: missing helper binaries, unsupported mount options, insufficient scratch space, or expected-output drift. Test signals: volatile paths, ids, device names, or tool output are filtered before golden comparison.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/065 -->
