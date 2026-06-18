<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/084 -->
# sources/test-tools/xfstests/tests/overlay/084

## Purpose
Advanced nested overlay xattr/whiteout test. It validates trusted/user overlay xattr escaping, nested mounts over escaped opaque directories, copy-up propagation of escaped xattrs, normal xwhiteouts, and escaped xwhiteouts inside nested overlay mounts.

## Important APIs, Types, And Functions
`_begin_fstest auto quick nested` declares xfstests groups/tags: auto, quick, nested. Imports `common/preamble`, `common/filter`, `common/attr`. Local helpers: `_cleanup()`, `umount_overlay()`, `test_escape()`, `do_test_xwhiteout()`, `test_xwhiteout()`, `test_escaped_xwhiteout()`. Feature gates/fix annotations include `_fixed_by_kernel_commit`, `_require_scratch_nocheck`, `_require_scratch_overlay_xattr_escapes`. External helper programs used include `$UMOUNT_PROG`.

## Control Flow
The test is a overlayfs export/file-handle regression test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 18: `$UMOUNT_PROG $OVL_BASE_SCRATCH_MNT/nested 2>/dev/null`; line 19: `rm -rf $tmp`; line 37: `_scratch_mkfs`; line 47: `$UMOUNT_PROG $SCRATCH_MNT`; line 62: `_scratch_mkfs`; line 63: `mkdir -p $lowerdir $middir $upperdir $workdir $nesteddir`; line 65: `_overlay_scratch_mount_dirs $lowerdir $middir $workdir $extra_options`; line 67: `mkdir -p $SCRATCH_MNT/layer1/dir/ $SCRATCH_MNT/layer2/dir`; line 69: `touch $SCRATCH_MNT/layer1/dir/file`; line 73: `setfattr -n user.overlay.opaque -v "y" $SCRATCH_MNT/layer2/dir`.

## State And Persistence
State is kept in shell variables such as `lowerdir`, `middir`, `upperdir`, `workdir`, `nesteddir`, `extra_options`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: file-handle behavior is sensitive to dcache warmth, inode identity, stale-handle semantics, and export feature availability; xattr and overlay metadata assertions depend on trusted/user xattr support and exact kernel on-disk semantics. Test signals: volatile paths, ids, device names, or tool output are filtered before golden comparison.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/084 -->
