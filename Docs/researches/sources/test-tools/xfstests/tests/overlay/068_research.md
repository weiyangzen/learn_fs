<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/068 -->
# sources/test-tools/xfstests/tests/overlay/068

## Purpose
Large nested-overlay file-handle test for samefs layers. It mounts overlay-on-overlay with NFS export enabled and exercises encode/decode/read/write across copy-up, unlink, hardlink, rename, directory rename, stored handle input/output, and dcache-pinned ancestors.

## Important APIs, Types, And Functions
`_begin_fstest auto quick copyup hardlink exportfs nested` declares xfstests groups/tags: auto, quick, copyup, hardlink, exportfs, nested. Imports `common/preamble`, `common/filter`. Local helpers: `_cleanup()`, `create_test_files()`, `test_file_handles()`, `create_dirs()`, `mount_dirs()`, `unmount_dirs()`. Feature gates/fix annotations include `_require_scratch`, `_require_test_program`, `_require_scratch_overlay_features`. External helper programs used include `$UMOUNT_PROG`, `open_by_handle`, `$here/src/open_by_handle`.

## Control Flow
The test is a overlayfs export/file-handle regression test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 29: `rm -f $tmp.*`; line 31: `$UMOUNT_PROG $mnt2 2>/dev/null`; line 62: `$here/src/open_by_handle -cp $opt $dir $NUMFILES`; line 73: `$here/src/open_by_handle $* $dir $NUMFILES`; line 80: `_scratch_mkfs`; line 83: `mkdir -p $upper2 $work2 $mnt2`; line 90: `_scratch_mount -o "index=on,nfs_export=on,redirect_dir=on"`; line 93: `_overlay_mount_dirs $SCRATCH_MNT $upper2 $work2 overlay2 $mnt2 \`; line 96: `_check_overlay_feature nfs_export overlay2 $mnt2`; line 103: `$UMOUNT_PROG $mnt2`.

## State And Persistence
State is kept in shell variables such as `upper2`, `work2`, `mnt2`, `lowerdir`, `upperdir`, `lowertestdir`, `uppertestdir`, `NUMFILES`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: file-handle behavior is sensitive to dcache warmth, inode identity, stale-handle semantics, and export feature availability; xattr and overlay metadata assertions depend on trusted/user xattr support and exact kernel on-disk semantics. Test signals: volatile paths, ids, device names, or tool output are filtered before golden comparison; unsupported environments are skipped with `_notrun`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/068 -->
