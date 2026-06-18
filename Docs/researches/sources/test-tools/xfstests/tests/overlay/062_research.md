<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/062 -->
# sources/test-tools/xfstests/tests/overlay/062

## Purpose
Regression test for decoding file handles from multiple lower layers on the same filesystem when the underlying lower dentry is pinned in dcache by a bind mount and is not from the uppermost lower layer.

## Important APIs, Types, And Functions
`_begin_fstest auto quick exportfs` declares xfstests groups/tags: auto, quick, exportfs. Imports `common/preamble`, `common/filter`. Local helpers: `_cleanup()`, `create_test_files()`, `test_file_handles()`. Feature gates/fix annotations include `_require_scratch`, `_require_test_program`, `_require_scratch_overlay_features`. External helper programs used include `$UMOUNT_PROG`, `open_by_handle`, `$here/src/open_by_handle`, `$MOUNT_PROG`.

## Control Flow
The test is a overlayfs export/file-handle regression test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 20: `rm -f $tmp.*`; line 21: `$UMOUNT_PROG $lowertestdir`; line 41: `mkdir -p $dir`; line 42: `$here/src/open_by_handle -cwp $dir $NUMFILES`; line 50: `$here/src/open_by_handle -rp $dir $NUMFILES`; line 53: `_scratch_mkfs`; line 63: `$MOUNT_PROG --bind $lowertestdir $lowertestdir`; line 66: `_overlay_scratch_mount_opts \`.

## State And Persistence
State is kept in shell variables such as `NUMFILES`, `lower`, `lower2`, `lowertestdir`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: file-handle behavior is sensitive to dcache warmth, inode identity, stale-handle semantics, and export feature availability; xattr and overlay metadata assertions depend on trusted/user xattr support and exact kernel on-disk semantics. Test signals: quiet success usually prints `Silence is golden`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/062 -->
