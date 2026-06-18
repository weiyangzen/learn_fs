<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/085 -->
# sources/test-tools/xfstests/tests/overlay/085

## Purpose
Variant of overlay/079 using the new `lowerdir+=` and `datadir+=` mount option syntax. It repeats no-access, absolute redirect follow, shared data-layer precedence, metacopy-to-data-copy transition, and lazy lowerdata lookup checks.

## Important APIs, Types, And Functions
`_begin_fstest auto quick metacopy redirect prealloc` declares xfstests groups/tags: auto, quick, metacopy, redirect, prealloc. Imports `common/preamble`, `common/filter`, `common/attr`. Local helpers: `check_metacopy()`, `check_redirect()`, `check_file_size()`, `check_file_blocks()`, `check_file_contents()`, `check_no_file_contents()`, `check_file_size_contents()`, `mount_overlay()`, `mount_ro_overlay()`, `umount_overlay()`, `test_no_access()`, `test_common()`, `test_lazy()`, `create_basic_files()`, and 1 more. Feature gates/fix annotations include `_require_scratch_nocheck`, `_require_scratch_overlay_features`, `_require_scratch_overlay_lowerdir_add_layers`, `_require_xfs_io_command`. External helper programs used include `$UMOUNT_PROG`, `$XFS_IO_PROG`.

## Control Flow
The test is a overlayfs data-only lower-layer behavior test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 26: `_scratch_mkfs`; line 143: `_overlay_scratch_mount_opts \`; line 153: `_overlay_scratch_mount_opts \`; line 160: `$UMOUNT_PROG $SCRATCH_MNT`; line 169: `stat $SCRATCH_MNT/$_target >> $seqres.full 2>&1 || \`; line 175: `stat $SCRATCH_MNT/$_target >> $seqres.full 2>&1 || \`; line 205: `chmod 400 $SCRATCH_MNT/$_target`; line 212: `$XFS_IO_PROG -c "falloc 0 1" $SCRATCH_MNT/$_target >> $seqres.full`; line 238: `_scratch_mkfs`; line 239: `mkdir -p $datadir/subdir $datadir2/subdir $lowerdir $lowerdir2 $upperdir $workdir $workdir2`.

## State And Persistence
State is kept in shell variables such as `dataname`, `sharedname`, `datacontent`, `dataname2`, `datacontent2`, `datasize`, `datarblocks`, `datarblocksize`, `estimated_datablocks`, `udirname`, `ufile`, `out_f`, and 13 more. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: xattr and overlay metadata assertions depend on trusted/user xattr support and exact kernel on-disk semantics. Test signals: volatile paths, ids, device names, or tool output are filtered before golden comparison.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/085 -->
