# File Research: sources/os/linux/linux-stable/fs/btrfs/tests/free-space-tree-tests.c

## Role
Tests on-disk free-space tree operations using a dummy single-leaf free-space tree root. Each logical operation is checked in both extent-item and bitmap-item formats, and then converted to the opposite format and checked again.

## Main Helpers
- `struct free_space_extent` describes expected free ranges.
- `__check_free_space_extents` reads `btrfs_free_space_info`, validates extent count and format flags, then verifies either extent items or bitmap bits match the expected ranges.
- `check_free_space_extents` performs a check, converts between extents and bitmaps, and checks the same logical ranges again.
- `run_test` creates dummy fs_info/root/block-group/transaction/path state, enables the free-space-tree compat-ro feature, initializes a leaf root node, adds block-group free space, optionally converts it to bitmap format, runs one test, removes block-group free space, and verifies no free-space tree items remain.
- `run_test_both_formats` runs each operation once starting from extents and once starting from bitmaps.

## Test Cases
- `test_empty_block_group` expects the whole block group to be free.
- `test_remove_all` removes all free space.
- `test_remove_beginning`, `test_remove_end`, and `test_remove_middle` remove aligned ranges at different positions and check resulting splits.
- `test_merge_left`, `test_merge_right`, and `test_merge_both` add adjacent regions in orders that should merge with left, right, or both neighbors.
- `test_merge_none` adds separated regions and verifies they remain separate.
- `btrfs_test_free_space_tree` runs every test at sectorsize alignment and at bitmap-page alignment (`BTRFS_FREE_SPACE_BITMAP_BITS * PAGE_SIZE`) to exercise bitmap handling across page-sized boundaries.

## Dependencies
Depends on free-space-tree internals, Btrfs item/key accessors, dummy transactions, dummy extent buffers, block group free-space tree hooks, and conversion between free-space extent and bitmap representations.
