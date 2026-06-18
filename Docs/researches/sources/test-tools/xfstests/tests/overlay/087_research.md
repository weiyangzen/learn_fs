<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/087 -->
# sources/test-tools/xfstests/tests/overlay/087

## Purpose
Overlayfs variant of an XFS syncfs-after-shutdown regression test. It checks that syncfs reports shutdown errors on a normal overlay over XFS, then repeats with `volatile` overlay where syncfs after shutdown is expected not to report the same error.

## Important APIs, Types, And Functions
`_begin_fstest auto quick mount shutdown` declares xfstests groups/tags: auto, quick, mount, shutdown. Imports `common/preamble`. Feature gates/fix annotations include `_require_scratch_nocheck`, `_require_scratch_shutdown_and_syncfs`, `_require_metadata_journaling`. External helper programs used include `xfs_fs_sync_fs`.

## Control Flow
The test is a overlayfs mount option validation test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 45: `_scratch_mount`; line 46: `_scratch_shutdown_and_syncfs`; line 49: `_scratch_unmount`; line 51: `_scratch_mount -o volatile`; line 52: `_scratch_shutdown_and_syncfs`.

## State And Persistence
State is mostly external to the script. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: uses disruptive kernel/storage state such as cache dropping, shutdown, dm-error, error injection, or crash/hang triggers. Test signals: unsupported environments are skipped with `_notrun`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/087 -->
