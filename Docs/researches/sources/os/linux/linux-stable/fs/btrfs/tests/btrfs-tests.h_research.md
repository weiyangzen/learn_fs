# File Research: sources/os/linux/linux-stable/fs/btrfs/tests/btrfs-tests.h

## Role
Shared header for Btrfs in-kernel self-tests. It declares the test runner, logging macros, allocation-error indexes, individual test entry points, and dummy object helpers when sanity tests are enabled.

## Main Interfaces
- Under `CONFIG_BTRFS_FS_RUN_SANITY_TESTS`, declares `btrfs_run_sanity_tests` and all test entry points for extent buffers, free-space cache, extent I/O, inodes, qgroups, free-space tree, raid stripe tree, extent maps, delayed refs, chunk allocation, and zoned testing.
- Defines `test_msg` and `test_err` logging macros with consistent `BTRFS: selftest` prefixes and file/line context for errors.
- Defines allocation-error enum values consumed by `test_error[]`.
- Declares dummy allocation/free helpers for inodes, fs_info, roots, block groups, transactions, and devices.
- Uses `DEFINE_FREE` wrappers for dummy fs_info and block groups to support kernel cleanup-attribute style automatic cleanup.
- Provides a no-op `btrfs_test_zoned` when zoned block device support is disabled, and a no-op `btrfs_run_sanity_tests` when the whole self-test config is disabled.

## Dependencies
Includes Linux types and cleanup helpers, and forward-declares Btrfs structures to keep test source files loosely coupled to the common harness.
