# File Research: sources/os/linux/linux/fs/btrfs/tests/btrfs-tests.h

Read completely: 83 lines.

This header exposes the Btrfs selftest API when `CONFIG_BTRFS_FS_RUN_SANITY_TESTS` is enabled.

It defines:
- `test_msg()` and `test_err()` logging macros with consistent `BTRFS: selftest:` prefixes.
- `test_std_err()` for common allocation failures.
- Allocation error enum values used as indices into `test_error[]`.
- Prototypes for all Btrfs selftest entry points.
- Prototypes for dummy fs_info, root, block-group, transaction, inode, and device helpers.
- `DEFINE_FREE()` cleanup helpers for dummy fs_info and dummy block groups.
- A zoned-test stub returning `0` when `CONFIG_BLK_DEV_ZONED` is disabled.
- A stub `btrfs_run_sanity_tests()` returning `0` when sanity tests are not compiled.

The header is the shared contract between the selftest runner and each individual test file.
