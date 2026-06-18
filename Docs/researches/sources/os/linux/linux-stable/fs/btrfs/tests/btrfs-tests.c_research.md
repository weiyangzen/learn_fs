# File Research: sources/os/linux/linux-stable/fs/btrfs/tests/btrfs-tests.c

## Role
Provides the common in-kernel Btrfs self-test harness. It creates a pseudo filesystem mount for test inodes, allocates and frees dummy Btrfs objects, initializes dummy transactions, and orchestrates the complete sanity-test suite.

## Main Interfaces and Data
- Defines `test_mnt`, the pseudo filesystem type `btrfs_test_fs`, and `btrfs_test_super_ops`.
- Defines `test_error[]`, a shared allocation-error message table used by `test_std_err`.
- Exports helpers: `btrfs_new_test_inode`, `btrfs_alloc_dummy_fs_info`, `btrfs_free_dummy_fs_info`, `btrfs_alloc_dummy_device`, `btrfs_free_dummy_root`, `btrfs_alloc_dummy_block_group`, `btrfs_free_dummy_block_group`, `btrfs_init_dummy_transaction`, and `btrfs_init_dummy_trans`.
- Exports `btrfs_run_sanity_tests`, the top-level test runner.

## Behavior
- `btrfs_init_test_fs` registers and mounts a pseudo filesystem using Btrfs inode allocation/destruction so tests can allocate real VFS inodes without a mounted Btrfs filesystem.
- Dummy fs_info allocation creates `struct btrfs_fs_info`, `struct btrfs_fs_devices`, and a superblock copy, calls `btrfs_init_fs_info`, sets nodesize/sectorsize/checksum parameters, marks the fs as dummy/testing, and attaches it to the pseudo superblock.
- Dummy cleanup releases extent buffers held in `buffer_tree`, frees mapping tree state, dummy devices, qgroup config, roots, superblock copy, and fs_devices, while also running root and extent-buffer leak debug checks.
- Dummy devices are linked into `fs_info->fs_devices->devices` and initialize their allocation extent I/O tree.
- Dummy block groups allocate a free-space control structure, initialize lists and the free-space cache, and set basic geometry.
- The sanity runner tests each supported nodesize for `PAGE_SIZE` sectorsize, running free-space cache, extent-buffer, extent I/O, inode, qgroup, free-space-tree, raid-stripe-tree, delayed-ref, and chunk-allocation tests, then runs extent-map and zoned tests.

## Dependencies
This harness depends on VFS pseudo filesystems, Btrfs inode lifecycle, fs_info initialization, free-space cache, free-space tree, transactions, volumes, disk I/O, qgroups, block groups, and root tracking.
