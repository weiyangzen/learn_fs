# File Research: sources/local-fs/kdave-linux/fs/btrfs/tests/free-space-tests.c

This file tests the in-memory free-space cache for block groups, including extent entries, bitmap entries, mixed extent/bitmap removals, bitmap-to-extent stealing, and the bytes index.

`test_extents()` validates basic extent-entry add/remove behavior: full removal, tail removal, front removal, middle removal, and absence checks for removed ranges.

`test_bitmaps()` forces bitmap entries and validates full bitmap removal, middle removal, and removal across two bitmap entries near the bitmap boundary.

`test_bitmaps_and_extents()` exercises mixed free-space representation: removing from extents while bitmaps exist, removing from bitmaps while extent entries exist, overlapping extent/bitmap removals, extent entries offset into bitmap coverage, and historical `-EAGAIN` style overlap regressions.

`test_steal_space_from_bitmap_to_extent()` replaces the free-space ops with a test `use_bitmap` policy to force bitmap creation. It validates that contiguous free space can be stolen from a bitmap into an adjacent extent entry so a large allocation can be satisfied by one entry. It tests both extent-left/bitmap-right and bitmap-left/extent-right layouts and ensures unrelated small bitmap regions are not stolen.

`check_num_extents_and_bitmaps()` and `check_cache_empty()` verify internal counters, remaining free space, allocation failure, and empty-cache state.

`test_bytes_index()` validates ordering of the free-space bytes index for extents and bitmaps, including bitmap `bytes` versus `max_extent_size` behavior after allocation searches recalculate the index.

`btrfs_test_free_space_cache()` builds dummy fs/root/block-group state large enough to cross bitmap boundaries, registers an extent-tree dummy root, and runs all free-space cache tests.
