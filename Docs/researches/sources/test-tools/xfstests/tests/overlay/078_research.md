<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/078 -->
# sources/test-tools/xfstests/tests/overlay/078

## Purpose
Copy-up of lower file attributes. It toggles `A`, `S`, `a`, and `i` flags on lower files, triggers copy-up with append writes or expected immutable write failure, optionally shuts down the scratch fs, cycles mounts, and confirms attribute preservation/removal.

## Important APIs, Types, And Functions
`_begin_fstest auto quick copyup perms shutdown` declares xfstests groups/tags: auto, quick, copyup, perms, shutdown. Imports `common/preamble`, `common/filter`. Local helpers: `_cleanup()`, `do_check()`. Feature gates/fix annotations include `_fixed_in_kernel_version`, `_require_command`, `_require_chattr`, `_require_xfs_io_command`, `_require_scratch`, `_require_scratch_shutdown`. External helper programs used include `$CHATTR_PROG`, `$LSATTR_PROG`, `$UMOUNT_PROG`, `$XFS_IO_PROG`.

## Control Flow
The test is a overlayfs regression test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 26: `$CHATTR_PROG -ai $lowertestfile &> /dev/null`; line 27: `$CHATTR_PROG -ai $uppertestfile &> /dev/null`; line 28: `rm -f $tmp.*`; line 51: `_scratch_mkfs`; line 52: `mkdir -p $lowerdir`; line 53: `touch $lowertestfile`; line 54: `_scratch_mount`; line 64: `$UMOUNT_PROG $SCRATCH_MNT`; line 67: `$CHATTR_PROG +$attr $lowertestfile`; line 70: `$CHATTR_PROG -ai $uppertestfile &> /dev/null`.

## State And Persistence
State is kept in shell variables such as `lowerdir`, `upperdir`, `workdir`, `lowertestfile`, `uppertestfile`, `testfile`, `attr`, `before`, `expect`, `result`, `after`, `opts`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: uses disruptive kernel/storage state such as cache dropping, shutdown, dm-error, error injection, or crash/hang triggers. Test signals: quiet success usually prints `Silence is golden`; volatile paths, ids, device names, or tool output are filtered before golden comparison.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/078 -->
