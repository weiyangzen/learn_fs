# File Research: sources/os/linux/linux/fs/btrfs/tests/btrfs-tests.c

Read completely: 313 lines.

This file implements the common in-kernel Btrfs selftest harness and dummy object allocation helpers.

Core harness:
- Registers a pseudo filesystem named `btrfs_test_fs` using `init_pseudo()` and `BTRFS_TEST_MAGIC`.
- Mounts it through `kern_mount()` so tests can allocate real VFS inodes.
- Provides `btrfs_new_test_inode()` to create regular-file test inodes backed by the pseudo superblock.
- `btrfs_run_sanity_tests()` initializes the pseudo filesystem, runs all configured Btrfs sanity tests over PAGE_SIZE sectorsize and every nodesize from sectorsize through `BTRFS_MAX_METADATA_BLOCKSIZE`, then runs extent-map and zoned tests.

Shared error strings:
- `test_error[]` maps common allocation failure categories to messages used by `test_std_err()`.

Dummy object helpers:
- `btrfs_alloc_dummy_fs_info()` allocates `fs_info`, `fs_devices`, and `super_copy`, initializes core Btrfs state, sets nodesize/sectorsize/csum fields, marks the fs as dummy/testing, and installs it in the pseudo superblock.
- `btrfs_free_dummy_fs_info()` frees extent buffers from `buffer_tree`, mapping tree state, dummy devices, qgroup config, roots, superblock copy, fs_devices, and leak-checks roots/extent buffers.
- `btrfs_alloc_dummy_device()` initializes a dummy device allocation-state extent tree and links it into `fs_devices->devices`.
- `btrfs_alloc_dummy_block_group()` creates a block group with free-space control, lists, mutex, full stripe length, and free-space cache initialization.
- `btrfs_init_dummy_transaction()` and `btrfs_init_dummy_trans()` create minimal transaction and transaction-handle structures for tests.

The runner calls, in order:
- free-space cache tests
- extent-buffer operation tests
- extent I/O tests
- inode tests
- qgroup tests
- free-space tree tests
- raid-stripe-tree tests
- delayed-ref tests
- chunk-allocation tests
- extent-map tests
- zoned tests, when enabled

Correctness notes:
- Dummy fs_info teardown refuses non-testing fs_info objects.
- Dummy roots that were inserted into the global root radix are expected to be freed through `btrfs_free_fs_roots`; non-radix roots are explicitly deleted/put.
- The pseudo mount is global to the selftest run, so tests share the same synthetic VFS substrate but allocate their own Btrfs state.
