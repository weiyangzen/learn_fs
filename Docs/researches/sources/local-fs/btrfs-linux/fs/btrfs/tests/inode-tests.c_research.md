# File Research: sources/local-fs/btrfs-linux/fs/btrfs/tests/inode-tests.c

This file tests inode extent lookup and outstanding-delalloc extent accounting. It builds synthetic subvolume-tree leaves directly and validates `btrfs_get_extent()` across inline, hole, regular, preallocated, compressed, split, and implied-hole ranges.

`insert_extent()` inserts a `BTRFS_EXTENT_DATA_KEY` file extent item into a dummy leaf and fills all relevant file-extent fields: type, disk bytenr, disk length, offset, num bytes, ram bytes, compression, encryption, and encoding. Inline extents include inline data length in the item size. `insert_inode_item_key()` inserts a blank inode item so searches beginning with a hole behave like real tree searches.

`setup_file_extents()` creates a deliberately complex layout scaled by sectorsize: an inline extent, implied hole, regular extents, split regular extents with explicit hole, prealloc extents, partially written prealloc extents, compressed extents, split compressed extents, a hole with no extent item, and a final regular extent.

`test_btrfs_get_extent()` first verifies an empty tree returns a hole. It then installs the synthetic layout and walks through it in order, checking each returned extent map's start, length, disk mapping, offset, flags, and compression type. It verifies inline extent rounding to sectorsize, regular mappings, explicit and implied holes, prealloc flags, compressed flags and compression IDs, offset adjustment for split extents, and returned hole length behavior.

`test_hole_first()` handles the specific case where the first file range is a hole before the first real extent. It inserts an inode item and a regular extent starting at sectorsize, then checks `btrfs_get_extent()` returns a leading hole followed by the real extent.

`test_extent_accounting()` validates `BTRFS_I(inode)->outstanding_extents` as delalloc ranges are added, split by clearing a sector-sized hole, merged again, extended beyond `BTRFS_MAX_EXTENT_SIZE`, split again, refilled, and finally cleared completely. It checks accounting stays aligned to Btrfs maximum extent segmentation rules.

`btrfs_test_inodes()` sets expected flag masks for compressed and prealloc extent maps, then runs `test_btrfs_get_extent()`, `test_hole_first()`, and `test_extent_accounting()`.
