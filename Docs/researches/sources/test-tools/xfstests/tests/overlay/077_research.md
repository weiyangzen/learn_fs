<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/077 -->
# sources/test-tools/xfstests/tests/overlay/077

## Purpose
Readdir cache invalidation test. It uses `t_dir_offset2` with a small getdents buffer on pure upper, impure upper, merge, and former-merge directories to catch stale cached entries after create/remove operations.

## Important APIs, Types, And Functions
`_begin_fstest auto quick dir` declares xfstests groups/tags: auto, quick, dir. Imports `common/preamble`, `common/filter`. Local helpers: `create_files()`. Feature gates/fix annotations include `_fixed_by_kernel_commit`, `_require_scratch_nocheck`. External helper programs used include `$UMOUNT_PROG`, `$here/src/t_dir_offset2`.

## Control Flow
The test is a overlayfs regression test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 35: `touch ${1}/${2}${n}`; line 40: `_scratch_mkfs`; line 48: `mkdir -p $lowerdir/merge $lowerdir/former $upperdir/pure $upperdir/impure`; line 54: `touch $lowerdir/f100`; line 56: `_scratch_mount`; line 61: `touch $SCRATCH_MNT/merge/m100`; line 63: `mv $SCRATCH_MNT/o* $SCRATCH_MNT/impure/`; line 64: `mv $SCRATCH_MNT/f100 $SCRATCH_MNT/former/`; line 68: `$UMOUNT_PROG $SCRATCH_MNT`; line 69: `rm -rf $lowerdir/former`.

## State And Persistence
State is kept in shell variables such as `bufsize`, `lowerdir`, `upperdir`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: main risk is environmental: missing helper binaries, unsupported mount options, insufficient scratch space, or expected-output drift. Test signals: quiet success usually prints `Silence is golden`; content or output comparison is a primary failure signal.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/077 -->
