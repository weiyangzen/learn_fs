<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/076 -->
# sources/test-tools/xfstests/tests/overlay/076

## Purpose
Dangerous regression test for directory `chattr +i` ioctl deadlock. It mounts a lower directory through overlay and runs `chattr +i`; failure is acceptable on unsupported kernels, but hanging indicates the v5.10 regression.

## Important APIs, Types, And Functions
`_begin_fstest auto quick perms dangerous` declares xfstests groups/tags: auto, quick, perms, dangerous. Imports `common/preamble`, `common/filter`. Local helpers: `_cleanup()`. Feature gates/fix annotations include `_require_scratch`, `_require_chattr`. External helper programs used include `$CHATTR_PROG`, `$UMOUNT_PROG`.

## Control Flow
The test is a overlayfs regression test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 21: `$CHATTR_PROG -i $lowerdir/foo > /dev/null 2>&1`; line 22: `$CHATTR_PROG -i $upperdir/foo > /dev/null 2>&1`; line 23: `rm -f $tmp.*`; line 33: `_scratch_mkfs`; line 39: `mkdir -p $lowerdir`; line 40: `mkdir $lowerdir/foo`; line 43: `_scratch_mount`; line 48: `$CHATTR_PROG +i $SCRATCH_MNT/foo > /dev/null 2>&1`; line 50: `$UMOUNT_PROG $SCRATCH_MNT`.

## State And Persistence
State is kept in shell variables such as `lowerdir`, `upperdir`, `workdir`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: marked dangerous, so it can crash, hang, or exercise kernel failure paths. Test signals: quiet success usually prints `Silence is golden`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/076 -->
