<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/054 -->
# sources/test-tools/xfstests/tests/overlay/054

## Purpose
Regression test for overlayfs NFS-export file handles when a merge directory or its ancestors were created before directory indexes existed. It creates lower and upper merge state, encodes handles for the merge dir, child, grandchild, and sibling child, renames the non-indexed merge dir, and checks that stored handles still decode/read or fail only in the expected lower-ancestor cases.

## Important APIs, Types, And Functions
`_begin_fstest auto quick copyup redirect exportfs` declares xfstests groups/tags: auto, quick, copyup, redirect, exportfs. Imports `common/preamble`, `common/filter`. Local helpers: `create_test_files()`, `test_file_handles()`, `create_dirs()`, `mount_dirs()`, `unmount_dirs()`. Feature gates/fix annotations include `_fixed_by_kernel_commit`, `_require_scratch`, `_require_test_program`, `_require_scratch_overlay_features`. External helper programs used include `open_by_handle`, `$here/src/open_by_handle`, `$UMOUNT_PROG`.

## Control Flow
The test is a overlayfs export/file-handle regression test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 60: `mkdir -p $dir`; line 61: `$here/src/open_by_handle -cp $opt $dir $NUMFILES`; line 72: `$here/src/open_by_handle $* $dir $NUMFILES`; line 78: `_scratch_mkfs`; line 84: `_scratch_mount -o "index=on,nfs_export=on,redirect_dir=on"`; line 90: `$UMOUNT_PROG $SCRATCH_MNT`; line 100: `mkdir $upper/merged`; line 119: `mv $SCRATCH_MNT/merged $SCRATCH_MNT/merged.new/`.

## State And Persistence
State is kept in shell variables such as `lower`, `upper`, `work`, `NUMFILES`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: file-handle behavior is sensitive to dcache warmth, inode identity, stale-handle semantics, and export feature availability; xattr and overlay metadata assertions depend on trusted/user xattr support and exact kernel on-disk semantics. Test signals: volatile paths, ids, device names, or tool output are filtered before golden comparison.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/054 -->
