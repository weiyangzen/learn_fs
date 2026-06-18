<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/060 -->
# sources/test-tools/xfstests/tests/overlay/060

## Purpose
Comprehensive metadata-only copy-up test. It covers lower files, midlayer metacopy files, rename redirects, link redirects, hardlink absolute redirects, read-only follow of lowerdata, and transition from metacopy xattr to full data copy-up after fallocate.

## Important APIs, Types, And Functions
`_begin_fstest auto quick metacopy redirect prealloc` declares xfstests groups/tags: auto, quick, metacopy, redirect, prealloc. Imports `common/preamble`, `common/filter`, `common/attr`. Local helpers: `check_metacopy()`, `check_redirect()`, `check_file_size()`, `check_file_blocks()`, `check_file_contents()`, `check_file_size_contents()`, `mount_overlay()`, `mount_ro_overlay()`, `umount_overlay()`, `test_common()`, `create_basic_files()`, `create_lower_link()`, `prepare_midlayer()`. Feature gates/fix annotations include `_require_scratch_nocheck`, `_require_scratch_overlay_features`, `_require_xfs_io_command`. External helper programs used include `$UMOUNT_PROG`, `$XFS_IO_PROG`.

## Control Flow
The test is a overlayfs data-only lower-layer behavior test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 23: `_scratch_mkfs`; line 121: `_overlay_scratch_mount_dirs "$_lowerdir" $upperdir $workdir -o redirect_dir=on,index=on,metacopy=on`; line 128: `_overlay_scratch_mount_dirs "$_lowerdir" "-" "-" -o ro,redirect_dir=follow,metacopy=on`; line 133: `$UMOUNT_PROG $SCRATCH_MNT`; line 155: `chmod 400 $SCRATCH_MNT/$_target`; line 163: `$XFS_IO_PROG -c "falloc 0 1" $SCRATCH_MNT/$_target >> $seqres.full`; line 173: `_scratch_mkfs`; line 174: `mkdir -p $lowerdir/subdir $lowerdir2 $upperdir $workdir $workdir2`; line 175: `mkdir -p $upperdir/$udirname`; line 177: `chmod 600 $lowerdir/$lowername`.

## State And Persistence
State is kept in shell variables such as `lowername`, `lowerlink`, `lowerdata`, `lowersize`, `lowerblocks`, `udirname`, `ufile`, `out_f`, `target_f`, `msg`, `value`, `actual_size`, and 6 more. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: xattr and overlay metadata assertions depend on trusted/user xattr support and exact kernel on-disk semantics. Test signals: volatile paths, ids, device names, or tool output are filtered before golden comparison.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/060 -->
