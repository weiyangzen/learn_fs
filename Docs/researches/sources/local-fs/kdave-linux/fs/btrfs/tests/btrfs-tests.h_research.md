# File Research: sources/local-fs/kdave-linux/fs/btrfs/tests/btrfs-tests.h

This header gates the Btrfs selftest API behind `CONFIG_BTRFS_FS_RUN_SANITY_TESTS`.

When selftests are enabled, it declares `btrfs_run_sanity_tests()`, logging helpers `test_msg()` and `test_err()`, standard allocation error indexes, the shared `test_error[]` table, all individual test entry points, and dummy allocation/cleanup helpers.

It declares test functions for extent buffers, free-space cache, extent I/O, inodes, qgroups, free-space tree, raid stripe tree, extent map, delayed refs, chunk allocation, and zoned mode.

It provides cleanup helpers through `DEFINE_FREE` for dummy fs info and dummy block groups, allowing local automatic cleanup in tests that use kernel cleanup annotations.

When selftests are disabled, `btrfs_run_sanity_tests()` is a no-op returning 0. When zoned support is disabled, `btrfs_test_zoned()` is also a no-op.
