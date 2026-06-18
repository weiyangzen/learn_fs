# File Research: sources/local-fs/btrfs-linux/fs/btrfs/tests/free-space-tests.c

This file tests the in-memory free-space cache for block groups. It covers extent-only free space, bitmap-only free space, mixed bitmap/extent operations, stealing contiguous bitmap space into extent entries, and the bytes-index ordering used for allocation search.

`test_extents()` adds and removes extent entries, checking complete removal plus front, tail, and middle removal cases. It uses `test_check_exists()` to ensure removed regions are actually gone.

`test_bitmaps()` forces bitmap entries and tests full removal, middle removal, and removal spanning two bitmap entries. Bitmap span uses `BITS_PER_BITMAP * sectorsize` to calculate the next bitmap boundary.

`test_bitmaps_and_extents()` covers mixed representation edge cases: extents and bitmaps at the same offset, removal fully in one representation, overlapping removal across both, an extent starting before a bitmap while deletion falls inside both, and a previous regression where removing a range split across bitmap and extent returned `-EAGAIN`.

`test_steal_space_from_bitmap_to_extent()` uses a custom `use_bitmap` operation to force bitmap use after at least one extent exists. It builds scenarios where an extent and bitmap represent adjacent free ranges, then verifies bitmap free space is stolen into the extent entry so a single large allocation can succeed. It tests both directions: extent on the left of a bitmap and extent on the right of a bitmap. It also ensures unrelated small bitmap free ranges are not stolen incorrectly and that the cache becomes empty after expected allocations.

`test_bytes_index()` validates the `free_space_bytes` rb-tree ordering. It first checks extent entries are sorted by descending byte size, then bitmap entries by byte size, then forces all new free space into bitmaps and validates the transition between indexing by total bytes and `max_extent_size` after failed allocation searches.

`btrfs_test_free_space_cache()` allocates a dummy fs_info and block group sized to cross bitmap boundaries even on large-page systems, inserts a dummy extent-tree root, then runs extent, bitmap, mixed, stealing, and bytes-index tests.
