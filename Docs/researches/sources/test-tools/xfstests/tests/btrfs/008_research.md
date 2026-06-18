## sources/test-tools/xfstests/tests/btrfs/008

Purpose: this quick send regression test checks a historical ENOENT failure path by sending a read-only snapshot with nested directories/files and receiving it onto scratch.

Control flow: it requires test and scratch filesystems, reformats scratch, disables `SELINUX_MOUNT_OPTIONS` so receive can set security xattrs, mounts scratch, creates a test-side subvolume `send`, populates directories and random files, creates two read-only snapshots `backup2` and `backup3`, sends `backup3` to a dump file, and receives it into scratch.

State and persistence: the source subvolume and snapshots are created under `TEST_DIR/send_temp_$seq`, while the receive target is scratch. Cleanup deletes snapshots/subvolumes and the temp directory.

Dependencies: `_require_test`, `_require_scratch`, `_scratch_mkfs`, `_scratch_mount`, `$BTRFS_UTIL_PROG subvolume/send/receive`, `_ddt`, and generic filters.

Risks: source data is created on `TEST_DIR`, so the test assumes the test filesystem itself is btrfs-capable enough for subvolume creation. SELinux option override is required for receive; without it, xattr restoration can fail. Cleanup assumes specific snapshot names exist but suppresses errors.

Test signals: the intended output is `Silence is golden`. Any failure in subvolume creation, snapshot, send, or receive triggers `_fail`.
