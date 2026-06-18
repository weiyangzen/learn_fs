# File Research: sources/os/linux/linux-stable/fs/btrfs/tests/inode-tests.c

## Role
Tests Btrfs inode extent lookup and outstanding delalloc extent accounting with a synthetic single-leaf file extent layout.

## Main Setup
- `insert_extent` writes a file extent item into a dummy leaf at a requested slot, supporting inline, regular, prealloc, explicit hole, and compressed extents.
- `insert_inode_item_key` inserts a minimal inode item key for hole-first lookup tests.
- `setup_file_extents` builds a complex ordered file layout starting with an inline extent, followed by implied and explicit holes, regular extents, split regular extents, prealloc extents, partially written prealloc extents, compressed extents, split compressed extents, and a final implied hole before a regular extent.
- Global expected flag masks `prealloc_only`, `compressed_only`, and `vacancy_only` are used for extent-map flag validation.

## Test Behavior
- `test_btrfs_get_extent` first checks that an inode with no extents returns a hole. It then installs the complex layout and walks it with `btrfs_get_extent`, validating each returned extent map's disk address class, logical start, length, flags, offset, physical block start, and compression type. It checks inline rounding to sectorsize, regular extents, explicit holes, split regular mappings, prealloc mappings, written portions of prealloc mappings, compressed mappings, split compressed mappings, implied holes, and the final regular extent after a hole.
- `test_hole_first` creates a leaf with an inode item and a regular extent starting at one sectorsize, then verifies lookup at zero returns a leading hole and lookup at the next sector returns the real extent.
- `test_extent_accounting` exercises `outstanding_extents` accounting by setting and clearing delalloc ranges around `BTRFS_MAX_EXTENT_SIZE`, introducing holes, refilling holes, creating separated large regions, merging them, and finally clearing all delalloc state back to zero.
- `btrfs_test_inodes` initializes expected compression/prealloc flags, runs extent lookup tests, hole-first tests, and outstanding-extent accounting.

## Dependencies
Depends on Btrfs inode extent lookup, extent-map flags and compression encoding, dummy roots and extent buffers, file extent item accessors, extent I/O tree delalloc state, and outstanding extent accounting.
