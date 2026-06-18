# File Research: sources/os/linux/linux/fs/btrfs/tests/inode-tests.c

Read completely: 1095 lines.

This file tests inode extent lookup and outstanding extent accounting.

Tree setup helpers:
- `insert_extent()` inserts a synthetic `BTRFS_EXTENT_DATA_KEY` item into a dummy level-0 root leaf, supporting inline, regular, prealloc, compressed, and explicit-hole file extent items.
- `insert_inode_item_key()` inserts a minimal inode item key used by the hole-first test.
- `setup_file_extents()` builds a dense synthetic file layout covering inline extents, implied holes, explicit holes, regular extents, split regular extents, prealloc extents, partially written prealloc extents, compressed extents, split compressed extents, and a final regular extent after a no-item hole.

`test_btrfs_get_extent()`:
- First verifies an empty tree returns `EXTENT_MAP_HOLE`.
- Then loads the complex extent layout and walks it with `btrfs_get_extent()`.
- It validates for each returned extent map:
  - `disk_bytenr` kind: inline, hole, or real physical extent
  - logical start and length
  - flags for prealloc and compressed extents
  - offset handling for split extents
  - physical block start adjustments
  - compression type for zlib compressed extents
- It specifically checks inline extent rounding to sectorsize, explicit holes, implied holes between extents, prealloc flags, compressed flags, and split compressed extent offsets.

`test_hole_first()`:
- Builds a tree where the first file range is a hole and a regular extent starts at sectorsize.
- Verifies `btrfs_get_extent()` returns a sectorsize-sized hole for `[0,sectorsize)` and then the expected real extent.

`test_extent_accounting()`:
- Exercises `btrfs_set_extent_delalloc()` and `btrfs_clear_extent_bit()` over large delalloc regions split around `BTRFS_MAX_EXTENT_SIZE`.
- Validates `BTRFS_I(inode)->outstanding_extents` as regions are added, split by holes, rejoined, split again, refilled, and finally cleared.
- Ensures large delalloc ranges are counted as the correct number of extent-sized units.

`btrfs_test_inodes()` sets expected flag masks for compressed and prealloc extents, then runs:
- `test_btrfs_get_extent()`
- `test_hole_first()`
- `test_extent_accounting()`

Correctness focus:
- `btrfs_get_extent()` must correctly translate on-disk file extent items into in-memory extent maps across inline, hole, regular, prealloc, and compressed cases.
- Offset and block-start math for split extents is heavily validated.
- Delalloc outstanding extent accounting must track logical splits and merges rather than just raw byte presence.
