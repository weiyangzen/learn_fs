# File Research: sources/local-fs/btrfs-linux/fs/btrfs/tests/btrfs-tests.c

This file is the shared selftest harness for Btrfs in-kernel sanity tests. It provides the pseudo filesystem mount used for test inodes, shared dummy object allocation helpers, and the top-level `btrfs_run_sanity_tests()` dispatcher.

The pseudo filesystem is registered as `btrfs_test_fs` with `BTRFS_TEST_MAGIC`. Its super operations use `btrfs_alloc_inode` and `btrfs_test_destroy_inode`, allowing tests to allocate normal Btrfs inodes without mounting a real filesystem. `btrfs_init_test_fs()` registers and kernel-mounts it; `btrfs_destroy_test_fs()` unmounts and unregisters it.

`btrfs_new_test_inode()` creates a regular inode from the test mount, assigns `BTRFS_FIRST_FREE_OBJECTID`, and initializes ownership. This is the common inode source for extent, extent-map, and inode tests.

`btrfs_alloc_dummy_fs_info()` creates a minimal `btrfs_fs_info`, `btrfs_fs_devices`, and superblock copy, initializes Btrfs fs-info internals, sets nodesize/sectorsize/checksum parameters, marks the fs as dummy/testing, and attaches it to the test superblock. `btrfs_free_dummy_fs_info()` performs broad cleanup: buffer tree extent buffers, mapping tree, dummy devices, qgroup config, fs roots, super copy, leak checks, fs devices, and the fs_info itself.

Device and block-group helpers create enough state for allocation tests. `btrfs_alloc_dummy_device()` initializes an allocation extent-io tree and links the device into `fs_devices->devices`; `btrfs_alloc_dummy_block_group()` allocates a block group plus free-space control and initializes list heads, free-space state, and locking.

Transaction helpers initialize dummy transaction handles and transaction objects for code paths that need delayed refs or free-space-tree transactions without a real running transaction.

`btrfs_run_sanity_tests()` runs the selected selftests for each nodesize from `PAGE_SIZE` up to `BTRFS_MAX_METADATA_BLOCKSIZE`, currently with sectorsize `PAGE_SIZE`. It runs free-space cache, extent-buffer operations, extent I/O, inode, qgroup, free-space tree, raid-stripe tree, delayed refs, and chunk allocation tests, then runs extent-map tests and zoned tests once. It stops at the first failure and always destroys the test filesystem.
