# File Research: sources/local-fs/kdave-linux/fs/btrfs/tests/btrfs-tests.c

This file is the Btrfs in-kernel selftest harness. It registers a pseudo filesystem, mounts it internally, allocates dummy filesystem state, and runs the configured suite of Btrfs sanity tests.

`btrfs_test_init_fs_context()`, `test_type`, `btrfs_init_test_fs()`, and `btrfs_destroy_test_fs()` create and destroy the pseudo mount used for test inodes. The test superblock uses `btrfs_alloc_inode` and `btrfs_test_destroy_inode`.

Dummy helpers include `btrfs_new_test_inode()`, `btrfs_alloc_dummy_fs_info()`, `btrfs_free_dummy_fs_info()`, `btrfs_alloc_dummy_device()`, `btrfs_alloc_dummy_block_group()`, `btrfs_free_dummy_block_group()`, `btrfs_init_dummy_trans()`, and `btrfs_init_dummy_transaction()`.

`btrfs_alloc_dummy_fs_info()` initializes minimal `fs_info`, `fs_devices`, superblock copy, nodesize/sectorsize fields, checksum sizing, dummy-state flags, and the pseudo superblock’s `s_fs_info`.

`btrfs_free_dummy_fs_info()` performs broad cleanup: buffer tree extent buffers, mapping tree, dummy devices, qgroup config, roots, leak checks, super copy, fs_devices, and `fs_info`.

`btrfs_run_sanity_tests()` is the suite entry point. It initializes the pseudo filesystem, iterates over PAGE_SIZE sector size and nodesizes up to `BTRFS_MAX_METADATA_BLOCKSIZE`, and runs free-space-cache, extent-buffer, extent-io, inode, qgroup, free-space-tree, raid-stripe-tree, delayed-ref, and chunk-allocation tests. It then runs extent-map and zoned tests.
