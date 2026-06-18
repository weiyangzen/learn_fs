<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/089 -->
# sources/test-tools/xfstests/tests/overlay/089

## Purpose
Userxattr/no-metacopy variant of the fs-verity lowerdata test. It verifies user.overlay metacopy/redirect metadata and `verity=off/on/require` behavior for verity, no-verity, wrong-digest, and missing-digest files in a data-only layer setup.

## Important APIs, Types, And Functions
`_begin_fstest auto quick metacopy redirect verity attr` declares xfstests groups/tags: auto, quick, metacopy, redirect, verity, attr. Imports `common/preamble`, `common/filter`, `common/attr`, `common/verity`. Local helpers: `check_metacopy()`, `check_verity()`, `check_redirect()`, `check_file_size()`, `check_file_contents()`, `check_file_size_contents()`, `check_io_error()`, `create_basic_files()`, `prepare_midlayer()`, `test_common()`, `mount_overlay()`, `umount_overlay()`. Feature gates/fix annotations include `_require_scratch_nocheck`, `_require_attrs`, `_require_scratch_overlay_features`, `_require_scratch_overlay_lowerdata_layers`, `_require_scratch_overlay_datadir_without_metacopy`, `_require_scratch_overlay_verity`. External helper programs used include `$UMOUNT_PROG`.

## Control Flow
The test is a overlayfs fs-verity behavior test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 30: `_scratch_mkfs`; line 161: `_scratch_mkfs`; line 162: `mkdir -p $lowerdir $lowerdir2 $upperdir $workdir $workdir2`; line 165: `mkdir $lowerdir/$subdir`; line 174: `chmod 600 $lowerdir/$subdir$f`; line 177: `_fsv_enable $lowerdir/$subdir$f`; line 188: `_overlay_scratch_mount_dirs $lowerdir $lowerdir2 $workdir2 -o redirect_dir=on,index=on,verity=on,metacopy=on`; line 190: `mv $SCRATCH_MNT/base/$f $SCRATCH_MNT/$f`; line 194: `_overlay_trusted_to_user $lowerdir2`; line 196: `rm -rf $lowerdir2/base`.

## State And Persistence
State is kept in shell variables such as `verityname`, `noverityname`, `wrongverityname`, `missingverityname`, `lowerdata`, `lowerdata2`, `lowerdata3`, `lowerdata4`, `lowersize`, `lowerdir`, `lowerdir2`, `upperdir`, and 10 more. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: xattr and overlay metadata assertions depend on trusted/user xattr support and exact kernel on-disk semantics. Test signals: volatile paths, ids, device names, or tool output are filtered before golden comparison.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/089 -->
