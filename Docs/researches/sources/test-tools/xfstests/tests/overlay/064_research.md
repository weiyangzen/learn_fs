<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/064 -->
# sources/test-tools/xfstests/tests/overlay/064

## Purpose
Verifies that `cap_setuid` file capabilities survive both ordinary copy-up and metacopy-triggered copy-up under overlayfs.

## Important APIs, Types, And Functions
`_begin_fstest auto quick copyup` declares xfstests groups/tags: auto, quick, copyup. Imports `common/preamble`, `common/filter`. Feature gates/fix annotations include `_require_scratch`, `_require_command`, `_require_scratch_overlay_features`. External helper programs used include `$SETCAP_PROG`, `$GETCAP_PROG`, `xfs_io`, `$XFS_IO_PROG`.

## Control Flow
The test is a overlayfs metadata-only copy-up behavior test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 21: `_scratch_mkfs`; line 29: `$SETCAP_PROG cap_setuid+ep ${lowerdir}/file1`; line 30: `$SETCAP_PROG cap_setuid+ep ${lowerdir}/file2`; line 32: `_scratch_mount "-o metacopy=on"`; line 37: `$XFS_IO_PROG -c "stat" ${SCRATCH_MNT}/file1 >>$seqres.full`; line 43: `chmod 000 ${SCRATCH_MNT}/file2`; line 46: `$XFS_IO_PROG -c "stat" ${SCRATCH_MNT}/file2 >>$seqres.full`.

## State And Persistence
State is kept in shell variables such as `lowerdir`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: xattr and overlay metadata assertions depend on trusted/user xattr support and exact kernel on-disk semantics. Test signals: volatile paths, ids, device names, or tool output are filtered before golden comparison.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/064 -->
