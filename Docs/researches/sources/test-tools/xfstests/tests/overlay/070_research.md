<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/070 -->
# sources/test-tools/xfstests/tests/overlay/070

## Purpose
Nested samefs xino/stable-inode regression test. It records inode numbers for directories, files, symlinks, links, device nodes, fifo, and socket, copies them up, renames them, drops caches, cycles mounts, and verifies `st_ino`, readdir `d_ino`, and `/proc/locks` identity remain consistent.

## Important APIs, Types, And Functions
`_begin_fstest auto quick copyup redirect nested` declares xfstests groups/tags: auto, quick, copyup, redirect, nested. Imports `common/preamble`, `common/filter`. Local helpers: `_cleanup()`, `create_dirs()`, `mount_dirs()`, `unmount_dirs()`, `create_test_files()`, `record_inode_numbers()`, `check_inode_numbers()`. Feature gates/fix annotations include `_fixed_in_kernel_version`, `_require_scratch_nocheck`, `_require_test_program`, `_require_command`, `_require_scratch_overlay_features`, `_require_loop`. External helper programs used include `$UMOUNT_PROG`, `af_unix`, `t_dir_type`, `$FLOCK_PROG`, `$XFS_IO_PROG`, `$here/src/af_unix`, `$here/src/t_dir_type`.

## Control Flow
The test is a overlayfs export/file-handle regression test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 27: `rm -f $tmp.*`; line 29: `$UMOUNT_PROG $mnt2 2>/dev/null`; line 63: `_scratch_mkfs`; line 66: `mkdir -p $upper2 $work2 $mnt2`; line 69: `$XFS_IO_PROG -f -c "truncate 128k" $lower/img >> $seqres.full 2>&1`; line 77: `_scratch_mount -o "index=on,nfs_export=on"`; line 85: `_overlay_mount_dirs $SCRATCH_MNT $upper2 $work2 overlay2 $mnt2 \`; line 96: `$UMOUNT_PROG $mnt2`; line 97: `_overlay_check_dirs $SCRATCH_MNT $upper2 $work2 \`; line 101: `$UMOUNT_PROG $SCRATCH_MNT`.

## State And Persistence
State is kept in shell variables such as `lower`, `upper`, `work`, `upper2`, `work2`, `mnt2`, `lowerdir`, `upperdir`, `lowertestdir`, `uppertestdir`, `loopdev`, `FILES`, and 1 more. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: uses disruptive kernel/storage state such as cache dropping, shutdown, dm-error, error injection, or crash/hang triggers; file-handle behavior is sensitive to dcache warmth, inode identity, stale-handle semantics, and export feature availability; xattr and overlay metadata assertions depend on trusted/user xattr support and exact kernel on-disk semantics. Test signals: quiet success usually prints `Silence is golden`; content or output comparison is a primary failure signal; unsupported environments are skipped with `_notrun`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/070 -->
