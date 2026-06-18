<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/056 -->
# sources/test-tools/xfstests/tests/overlay/056

## Purpose
Validates `fsck.overlay` repair of missing `trusted.overlay.impure` xattrs. It removes impure xattrs from upper directories that contain origin targets, redirected children, or merge directories, runs non-destructive fsck with `-p`, and confirms the xattr is restored.

## Important APIs, Types, And Functions
`_begin_fstest auto quick fsck` declares xfstests groups/tags: auto, quick, fsck. Imports `common/preamble`, `common/filter`, `common/attr`. Local helpers: `make_redirect_dir()`, `remove_impure()`, `check_impure()`, `make_test_dirs()`. Feature gates/fix annotations include `_require_scratch_nocheck`, `_require_attrs`, `_require_command`. External helper programs used include `$FSCK_OVERLAY_PROG`, `$SETFATTR_PROG`, `$UMOUNT_PROG`.

## Control Flow
The test is a overlayfs xattr/redirect/whiteout behavior test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 23: `_scratch_mkfs`; line 31: `mkdir -p $target`; line 32: `$SETFATTR_PROG -n $OVL_XATTR_REDIRECT -v $value $target`; line 40: `$SETFATTR_PROG -x $OVL_XATTR_IMPURE $target`; line 62: `rm -rf $lowerdir $lowerdir2 $upperdir $workdir`; line 63: `mkdir -p $lowerdir $lowerdir2 $upperdir $workdir`; line 69: `mkdir $lowerdir/{testdir1,testdir2}`; line 70: `mkdir $upperdir/{testdir1,testdir2}`; line 71: `touch $lowerdir/testdir1/foo`; line 72: `mkdir $lowerdir/testdir2/subdir`.

## State And Persistence
State is kept in shell variables such as `OVL_XATTR_IMPURE_VAL`, `value`, `lowerdir`, `lowerdir2`, `upperdir`, `workdir`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: xattr and overlay metadata assertions depend on trusted/user xattr support and exact kernel on-disk semantics. Test signals: exit status and golden stdout comparison.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/056 -->
