<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/069 -->
# sources/test-tools/xfstests/tests/overlay/069

## Purpose
Non-samefs variant of overlay/068. The lower overlay lower layer lives on the test filesystem while upper/work live on scratch; the nested overlay then repeats the same file-handle, copy-up, link, unlink, move, and rename scenarios.

## Important APIs, Types, And Functions
`_begin_fstest auto quick copyup hardlink exportfs nested nonsamefs` declares xfstests groups/tags: auto, quick, copyup, hardlink, exportfs, nested, nonsamefs. Imports `common/preamble`, `common/filter`. Local helpers: `_cleanup()`, `create_test_files()`, `test_file_handles()`, `create_dirs()`, `mount_dirs()`, `unmount_dirs()`. Feature gates/fix annotations include `_require_test`, `_require_scratch_nocheck`, `_require_test_program`, `_require_scratch_overlay_features`. External helper programs used include `$UMOUNT_PROG`, `open_by_handle`, `$here/src/open_by_handle`.

## Control Flow
The test is a overlayfs export/file-handle regression test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 29: `rm -f $tmp.*`; line 31: `$UMOUNT_PROG $mnt2 2>/dev/null`; line 68: `$here/src/open_by_handle -cp $opt $dir $NUMFILES`; line 79: `$here/src/open_by_handle $* $dir $NUMFILES`; line 86: `_scratch_mkfs`; line 89: `rm -rf $lower $upper2 $work2 $mnt2`; line 90: `mkdir $lower $upper2 $work2 $mnt2`; line 97: `_overlay_mount_dirs $lower $upper $work overlay1 $SCRATCH_MNT \`; line 101: `_overlay_mount_dirs $SCRATCH_MNT $upper2 $work2 overlay2 $mnt2 \`; line 104: `_check_overlay_feature nfs_export overlay2 $mnt2`.

## State And Persistence
State is kept in shell variables such as `lower`, `upper`, `work`, `upper2`, `work2`, `mnt2`, `lowerdir`, `upperdir`, `lowertestdir`, `uppertestdir`, `NUMFILES`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: file-handle behavior is sensitive to dcache warmth, inode identity, stale-handle semantics, and export feature availability; xattr and overlay metadata assertions depend on trusted/user xattr support and exact kernel on-disk semantics. Test signals: volatile paths, ids, device names, or tool output are filtered before golden comparison; unsupported environments are skipped with `_notrun`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/069 -->
