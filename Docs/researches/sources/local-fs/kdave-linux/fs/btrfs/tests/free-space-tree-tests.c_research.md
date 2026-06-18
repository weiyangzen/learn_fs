# File Research: sources/local-fs/kdave-linux/fs/btrfs/tests/free-space-tree-tests.c

This file tests the on-disk-style free-space tree operations using dummy Btrfs tree state.

`__check_free_space_extents()` validates the free-space tree against an expected list of free ranges. It supports both extent-item format and bitmap format, reading `BTRFS_FREE_SPACE_EXTENT_KEY` items or walking bitmap bits with `btrfs_free_space_test_bit()`.

`check_free_space_extents()` first checks the current representation, then converts to the opposite representation with `btrfs_convert_free_space_to_extents()` or `btrfs_convert_free_space_to_bitmaps()` and checks again.

Individual test functions cover an empty block group, removing all free space, removing from the beginning, removing from the end, removing from the middle, merging left, merging right, merging both sides, and intentionally not merging separated ranges.

`run_test()` builds dummy fs/root/block-group state, enables the free-space-tree compat_ro feature, creates a single-level root node, adds initial block-group free space, optionally converts it to bitmaps, runs one test, removes block-group free space, and verifies no tree items remain.

`run_test_both_formats()` runs each operation starting from extent format and bitmap format.

`btrfs_test_free_space_tree()` runs all operations at sectorsize alignment and at a bitmap/page-derived alignment intended to flush out highmem/bitmap extent-buffer issues.
