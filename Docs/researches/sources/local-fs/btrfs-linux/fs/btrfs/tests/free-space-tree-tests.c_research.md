# File Research: sources/local-fs/btrfs-linux/fs/btrfs/tests/free-space-tree-tests.c

This file tests the on-disk free-space tree representation using dummy roots, dummy transactions, and synthetic block groups. It verifies both extent-item and bitmap-item formats and converts between them during validation.

`__check_free_space_extents()` reads the free-space info item for a block group and validates expected free-space extents. If the tree uses bitmaps, it walks bitmap items sector by sector and reconstructs free ranges from set bits. If it uses extent items, it checks item count, key type, objectid, and length directly.

`check_free_space_extents()` first validates the current representation, then flips to the other representation with `btrfs_convert_free_space_to_extents()` or `btrfs_convert_free_space_to_bitmaps()` and validates again. This means each functional test checks both encodings.

The individual test functions cover an empty block group, removing all free space, removing from the beginning, removing from the end, removing the middle, merging with a left neighbor, merging with a right neighbor, merging both neighbors, and adding non-adjacent extents without merging.

`run_test()` creates a dummy fs_info/root, enables the free-space-tree compat-ro flag, initializes a leaf root node, creates a dummy block group with a length of eight alignment units, marks it as needing free-space setup, adds its free space to the tree, optionally converts to bitmap format, runs one test, removes the block group free-space items, and asserts the root leaf has no leftover items.

`run_test_both_formats()` executes each test starting from extent format and bitmap format. `btrfs_test_free_space_tree()` runs all scenarios twice per format: once aligned to sectorsize and once aligned to `BTRFS_FREE_SPACE_BITMAP_BITS * PAGE_SIZE` to exercise extent-buffer bitmap handling around page boundaries.
