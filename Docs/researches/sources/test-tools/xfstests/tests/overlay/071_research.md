<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/071 -->
# sources/test-tools/xfstests/tests/overlay/071

## Purpose
Nested non-samefs xino/stable-inode variant. It excludes directories because nested xino cannot guarantee persistent directory inode numbers, then validates inode identity for non-directory file types across copy-up, rename, cache drop, and mount cycle.

## Important APIs, Types, And Functions
`_begin_fstest auto quick copyup redirect nested nonsamefs` declares xfstests groups/tags: auto, quick, copyup, redirect, nested, nonsamefs. Imports `common/preamble`, `common/filter`. Local helpers: `_cleanup()`, `create_dirs()`, `mount_dirs()`, `unmount_dirs()`, `create_test_files()`, `record_inode_numbers()`, `check_inode_numbers()`. Feature gates/fix annotations include `_fixed_in_kernel_version`, `_require_test`, `_require_scratch_nocheck`, `_require_test_program`, `_require_command`, `_require_scratch_overlay_features`, `_require_loop`. External helper programs used include `$UMOUNT_PROG`, `af_unix`, `t_dir_type`, `$FLOCK_PROG`, `$XFS_IO_PROG`, `$here/src/af_unix`, `$here/src/t_dir_type`.

## Control Flow
The test is a overlayfs export/file-handle regression test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 30: `rm -f $tmp.*`; line 32: `$UMOUNT_PROG $mnt2 2>/dev/null`; line 68: `_scratch_mkfs`; line 71: `rm -rf $lower $upper2 $work2 $mnt2`; line 72: `mkdir $lower $upper2 $work2 $mnt2`; line 75: `$XFS_IO_PROG -f -c "truncate 128k" $lower/img >> $seqres.full 2>&1`; line 83: `_overlay_mount_dirs $lower $upper $work overlay1 $SCRATCH_MNT \`; line 95: `_overlay_mount_dirs $SCRATCH_MNT $upper2 $work2 overlay2 $mnt2 \`; line 106: `$UMOUNT_PROG $mnt2`; line 107: `_overlay_check_dirs $SCRATCH_MNT $upper2 $work2 \`.

## State And Persistence
State is kept in shell variables such as `lower`, `upper`, `work`, `upper2`, `work2`, `mnt2`, `lowerdir`, `upperdir`, `lowertestdir`, `uppertestdir`, `loopdev`, `FILES`, and 1 more. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: uses disruptive kernel/storage state such as cache dropping, shutdown, dm-error, error injection, or crash/hang triggers; file-handle behavior is sensitive to dcache warmth, inode identity, stale-handle semantics, and export feature availability; xattr and overlay metadata assertions depend on trusted/user xattr support and exact kernel on-disk semantics. Test signals: quiet success usually prints `Silence is golden`; content or output comparison is a primary failure signal; unsupported environments are skipped with `_notrun`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/071 -->
