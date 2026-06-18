# File Research: sources/local-fs/btrfs-linux/fs/btrfs/tests/btrfs-tests.h

This header is the shared contract for Btrfs selftests. Under `CONFIG_BTRFS_FS_RUN_SANITY_TESTS`, it declares `btrfs_run_sanity_tests()`, the `test_msg()` and `test_err()` logging macros, standard allocation-error indexes, and `extern const char *test_error[]`.

It declares all major test entry points: extent-buffer operations, free-space cache, extent I/O, inode behavior, qgroups, free-space tree, raid-stripe tree, extent map, delayed refs, and chunk allocation. It also declares helper constructors and destructors for test inodes, dummy fs_info, dummy roots, dummy block groups, dummy devices, and dummy transactions.

The header uses `DEFINE_FREE()` cleanup helpers for dummy fs_info and block groups, matching the kernel cleanup attribute pattern used elsewhere.

Zoned tests are conditionally declared under `CONFIG_BLK_DEV_ZONED`; otherwise `btrfs_test_zoned()` is an inline success. If sanity tests are disabled entirely, `btrfs_run_sanity_tests()` becomes an inline no-op returning success.
