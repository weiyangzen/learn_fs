# File Research: sources/os/linux/linux/fs/btrfs/tests/free-space-tree-tests.c

Read completely: 586 lines.

This file tests the on-disk free-space tree update logic using dummy roots, block groups, and transactions.

Validation:
- `__check_free_space_extents()` reads the free-space info item and verifies expected extents in either extent-item format or bitmap format.
- For bitmap format, it walks bitmap keys and tests each sectorsize-aligned bit with `btrfs_free_space_test_bit()`.
- For extent format, it verifies item count and each `BTRFS_FREE_SPACE_EXTENT_KEY`.
- `check_free_space_extents()` validates the current format, converts to the opposite format, and validates again.

Test scenarios:
- `test_empty_block_group()` expects the whole block group to be free.
- `test_remove_all()` removes all free space.
- `test_remove_beginning()` removes the first aligned unit.
- `test_remove_end()` removes the last aligned unit.
- `test_remove_middle()` creates two free extents around a removed middle range.
- `test_merge_left()` adds adjacent space to the right of an existing range and expects merge.
- `test_merge_right()` adds adjacent space to the left and expects merge.
- `test_merge_both()` fills a gap between two ranges and expects one merged range.
- `test_merge_none()` adds separated ranges and expects no merge.

`run_test()` creates a dummy free-space-tree root, dummy block group, dummy transaction handle, path, and initial free-space tree entry. It optionally converts initial representation to bitmaps, runs a test, removes the block group free-space items, and verifies the root leaf has no leftover items.

`run_test_both_formats()` runs each scenario starting from extent format and bitmap format.

`btrfs_test_free_space_tree()` runs all scenarios with two alignments:
- sectorsize alignment
- `BTRFS_FREE_SPACE_BITMAP_BITS * PAGE_SIZE`, chosen to exercise extent-buffer bitmap handling around page boundaries and highmem-sensitive paths

Correctness focus:
- Free-space tree add/remove operations must produce identical logical free extents in extent and bitmap formats.
- Conversion between formats must preserve exact free-space state.
- Block-group free-space teardown must remove all items from the free-space tree.
