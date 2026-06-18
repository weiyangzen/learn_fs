## sources/test-tools/xfstests/tests/btrfs/010

Purpose: this delayed allocation accounting regression test checks that many outstanding extents merged into one do not leak btrfs metadata reservation.

Control flow: it requires a mounted test filesystem and btrfs sysfs, writes 32K separated 4K extents to `$TEST_DIR/$seq`, writes the 32K gaps to force extent merging while reservations exist, runs `sync`, finds the filesystem UUID with `findmnt`, enters `/sys/fs/btrfs/$uuid/allocation`, and prints a leak message only if `metadata/bytes_may_use - global_rsv_reserved` is nonzero.

State and persistence: it creates one large test file and removes it in cleanup. It reads btrfs sysfs allocation counters and writes no scratch state.

Dependencies: `_require_test`, `_require_btrfs_fs_sysfs`, `$XFS_IO_PROG`, `findmnt`, sysfs btrfs allocation files, and shell arithmetic.

Risks: the loop performs 65,536 xfs_io invocations, so it is slow and sensitive to filesystem size. The sysfs counter expression assumes `bytes_may_use` and `global_rsv_reserved` semantics remain comparable. Cleanup removes the file but not partial sysfs state because none is created.

Test signals: success prints `0 bytes leaked` filtered away by `grep -v`, followed by `Silence is golden`. Any nonzero leak line is a regression signal.
