<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/837 -->
# sources/test-tools/xfstests/tests/xfs/837

Purpose: verifies mount, remount, write rejection, and unmount behavior when an external XFS realtime device is marked read-only.

Important APIs, types, and functions: uses `blockdev --setro/--setrw`, `_scratch_mkfs '-d rtinherit'`, `_try_scratch_mount`, `_scratch_remount rw`, `_scratch_unmount`, and filtering helpers for read-only mount messages.

Control flow: require realtime and external local scratch rtdev, register cleanup to restore read-write, format with rtinherit, select an output variant for old quota behavior, mark the rt device read-only, try mounting, attempt a direct write, try remounting rw, and unmount.

State and persistence behavior: changes the block device readonly flag and restores it in cleanup. Scratch filesystem data is temporary.

Dependencies and integration points: depends on external `$SCRATCH_RTDEV`, blockdev, XFS realtime support, and kernel behavior fixed by commit `bfecc4091e07`.

Risks and test signals: quota mount options on non-metadir filesystems can cause expected EPERM, captured via `837.cfg`. Signals are filtered mount/write/remount outcomes and final `*** done`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/837 -->
