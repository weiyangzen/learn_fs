# File Research: sources/os/linux/linux-stable/fs/btrfs/tests/free-space-tests.c

## Role
Tests the in-memory Btrfs free-space cache, including extent entries, bitmap entries, mixed extent/bitmap interactions, bitmap-to-extent stealing, and bytes-index ordering used by allocation.

## Main Tests
- `test_extents` validates basic extent-only add/remove behavior: full removal, tail removal, front removal, middle removal, and no lingering space.
- `test_bitmaps` validates bitmap-only full removal, middle removal, and a removal crossing two bitmap regions.
- `test_bitmaps_and_extents` exercises mixed representations at same or overlapping offsets, removal from extent and bitmap entries, removal where extents and bitmaps overlap, extent-before-bitmap overlaps, and a previous `-EAGAIN` overlap case.
- `test_steal_space_from_bitmap_to_extent` forces bitmap use after at least one extent entry, constructs adjacent extent/bitmap free-space ranges, and verifies the cache can steal contiguous bitmap free space into an extent entry so a 1 MiB allocation can be served as a single allocation. It tests both extent-left-of-bitmap and extent-right-of-bitmap layouts and confirms unrelated small bitmap free ranges are not stolen.
- `test_bytes_index` validates `free_space_bytes` ordering for extent entries and bitmap entries, then checks bitmap reindexing from total bytes to `max_extent_size` after an allocation search and back to total bytes after more space is added.

## Entry Point
`btrfs_test_free_space_cache` allocates dummy fs_info, a block group large enough to cross bitmap boundaries on large-page systems, and a dummy extent-tree root. It inserts the root globally, runs all free-space cache tests, then frees block group, root, and fs_info state.

## Dependencies
Uses the free-space cache implementation, block group state, test-only free-space insertion/check helpers, Btrfs root registration, and the common dummy object harness.
