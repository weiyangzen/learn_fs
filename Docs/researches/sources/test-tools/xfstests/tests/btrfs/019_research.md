## sources/test-tools/xfstests/tests/btrfs/019

Purpose: this quick send regression test targets kernel bugzilla 60673, where incremental send could fail when identical directory contents were recreated in a different order with different inode numbers.

Control flow: it requires test and scratch filesystems, disables SELinux mount options for receive, mounts scratch, creates a source subvolume under `TEST_DIR`, builds a directory tree, snapshots it read-only as `snap1`, sends and receives it, deletes/recreates the tree in a different creation order, snapshots as `snap2`, sends an incremental stream from `snap1` to `snap2`, and receives it.

State and persistence: source subvolume, snapshots, and send dumps live under `TEST_DIR/send_temp_$seq`; received snapshots land on scratch. Cleanup deletes all subvolumes and temp files.

Dependencies: `$BTRFS_UTIL_PROG subvolume/send/receive`, `_require_test`, `_require_scratch`, `_scratch_mkfs`, `_scratch_mount`, and generic filters.

Risks: like btrfs/008, the source side assumes `TEST_DIR` supports btrfs subvolumes. The test validates successful receive but does not do a content checksum; the recreated topology is simple enough that receive success is the regression signal.

Test signals: expected output is `Silence is golden`; any send/receive or snapshot command failure triggers `_fail`.
