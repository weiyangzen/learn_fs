<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/063 -->
# sources/test-tools/xfstests/tests/overlay/063

## Purpose
Whiteout/negative-dentry regression test. It removes a lower file through overlay to create a whiteout, populates a cached negative dentry, deletes the upper whiteout behind the overlay, and creates a directory at the same name to ensure no crash.

## Important APIs, Types, And Functions
`_begin_fstest auto quick whiteout` declares xfstests groups/tags: auto, quick, whiteout. Imports `common/preamble`, `common/filter`. Feature gates/fix annotations include `_fixed_by_kernel_commit`, `_require_scratch`. External helper programs used include `$UMOUNT_PROG`.

## Control Flow
The test is a overlayfs xattr/redirect/whiteout behavior test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 24: `_scratch_mkfs`; line 29: `mkdir -p $lowerdir`; line 30: `touch ${lowerdir}/file`; line 32: `_scratch_mount`; line 35: `rm ${SCRATCH_MNT}/file`; line 39: `rm ${upperdir}/file`; line 40: `mkdir ${SCRATCH_MNT}/file > /dev/null 2>&1`; line 43: `$UMOUNT_PROG $SCRATCH_MNT`.

## State And Persistence
State is kept in shell variables such as `lowerdir`, `upperdir`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: xattr and overlay metadata assertions depend on trusted/user xattr support and exact kernel on-disk semantics. Test signals: quiet success usually prints `Silence is golden`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/063 -->
