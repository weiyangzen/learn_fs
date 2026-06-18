# File Research: sources/local-fs/kdave-linux/fs/btrfs/tests/inode-tests.c

This file tests inode extent lookup and outstanding extent accounting.

`insert_extent()` inserts synthetic file extent items into a dummy leaf. It can create inline, regular, preallocated, hole, compressed, and split file extents by setting all relevant `btrfs_file_extent_item` fields.

`setup_file_extents()` creates a deliberately complex file layout: inline data, implied hole, regular extents, explicit hole, split regular extents, prealloc extents, partially written prealloc extents, compressed extents, split compressed extents, regular extents, a larger implied hole with no file extent item, and a final regular extent.

`test_btrfs_get_extent()` first validates an empty inode returns a hole. It then uses the synthetic layout and repeatedly calls `btrfs_get_extent()` to verify returned `extent_map` start, length, disk bytenr, block start, offset, flags, compression type, prealloc state, compressed state, inline rounding, explicit holes, and implied holes.

`test_hole_first()` validates a file whose first file extent starts after offset 0. It expects `btrfs_get_extent()` to return a leading hole followed by the real extent.

`test_extent_accounting()` validates `BTRFS_I(inode)->outstanding_extents` accounting as delalloc ranges are added, split by clearing sectorsize holes, merged by refilling holes, expanded across `BTRFS_MAX_EXTENT_SIZE`, and finally fully cleared.

Global expected flag masks are initialized in `btrfs_test_inodes()`: compressed extents expect `EXTENT_FLAG_COMPRESS_ZLIB`, and prealloc extents expect `EXTENT_FLAG_PREALLOC`.

`btrfs_test_inodes()` runs extent lookup, hole-first lookup, and outstanding extent accounting for each sectorsize/nodesize combination supplied by the main harness.
