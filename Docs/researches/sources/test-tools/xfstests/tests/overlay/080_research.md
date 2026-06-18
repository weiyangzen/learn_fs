<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/080 -->
# sources/test-tools/xfstests/tests/overlay/080

## Purpose
Overlayfs fs-verity test for metacopy and data-only layers. It creates verity, no-verity, wrong-digest, and missing-digest data files, verifies `verity=off/on/require` behavior, checks I/O errors for invalid data, and verifies verity digest propagation/removal during metacopy and data copy-up.

## Important APIs, Types, And Functions
`_begin_fstest auto quick metacopy redirect verity` declares xfstests groups/tags: auto, quick, metacopy, redirect, verity. Imports `common/preamble`, `common/filter`, `common/attr`, `common/verity`. Local helpers: `check_metacopy()`, `check_verity()`, `check_redirect()`, `check_file_size()`, `check_file_contents()`, `check_file_size_contents()`, `check_io_error()`, `create_basic_files()`, `prepare_midlayer()`, `test_common()`, `mount_overlay()`, `umount_overlay()`. Feature gates/fix annotations include `_require_scratch_nocheck`, `_require_scratch_overlay_features`, `_require_scratch_overlay_lowerdata_layers`, `_require_scratch_overlay_verity`. External helper programs used include `$UMOUNT_PROG`.

## Control Flow
The test is a overlayfs fs-verity behavior test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 26: `_scratch_mkfs`; line 157: `_scratch_mkfs`; line 158: `mkdir -p $lowerdir $lowerdir2 $upperdir $workdir $workdir2`; line 161: `mkdir $lowerdir/$subdir`; line 170: `chmod 600 $lowerdir/$subdir$f`; line 173: `_fsv_enable $lowerdir/$subdir$f`; line 189: `_overlay_scratch_mount_dirs $lowerdir $lowerdir2 $workdir2 -o redirect_dir=on,index=on,verity=on,metacopy=on`; line 192: `mv $SCRATCH_MNT/base/$f $SCRATCH_MNT/$f`; line 194: `chmod 400 $SCRATCH_MNT/$f`; line 200: `rm -rf $lowerdir2/base`.

## State And Persistence
State is kept in shell variables such as `verityname`, `noverityname`, `wrongverityname`, `missingverityname`, `lowerdata`, `lowerdata2`, `lowerdata3`, `lowerdata4`, `lowersize`, `lowerdir`, `lowerdir2`, `upperdir`, and 10 more. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: xattr and overlay metadata assertions depend on trusted/user xattr support and exact kernel on-disk semantics. Test signals: volatile paths, ids, device names, or tool output are filtered before golden comparison.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/080 -->
