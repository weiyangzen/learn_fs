## sources/test-tools/xfstests/tests/btrfs/015

Purpose: this quick snapshot/remount regression test verifies that a filesystem mounted read-only and then remounted read-write can still create snapshots.

Control flow: it requires scratch, formats it, mounts with `-o ro`, remounts with `-o rw,remount`, and creates a snapshot of the scratch root at `$SCRATCH_MNT/snap`.

State and persistence: scratch contains the created `snap` subvolume. Mount state transitions from ro to rw in place.

Dependencies: `_scratch_mkfs`, `_scratch_mount`, `$BTRFS_UTIL_PROG subvolume snapshot`, and generic filters.

Risks: `_scratch_mount -o rw,remount` relies on the helper passing mount arguments in a way accepted by util-linux and btrfs. The test does not explicitly check mount flags after remount; snapshot success is the proof.

Test signals: success prints `Silence is golden`; failure is inability to create the snapshot after remount.
