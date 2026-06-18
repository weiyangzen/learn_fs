# File Research: sources/local-fs/btrfs-linux/fs/btrfs/tests/extent-map-tests.c

This file tests extent-map tree insertion, EEXIST conflict handling, extent-map dropping/splitting, pinned extent behavior, compressed overlap adjustment, and reverse physical-to-logical mapping.

`free_extent_map_tree()` removes all extent maps from an inode tree and, under debug builds, detects leaked references before force-resetting refs for cleanup.

Test cases 1 through 4 model races where concurrent reads/writes add overlapping or broader extent maps. They validate that `btrfs_add_extent_mapping()` returns the correct existing or adjusted extent map rather than failing incorrectly when the desired range is already covered. These include regular extents, inline extents, buffered write overlap, and DIO split overlap scenarios.

`test_case_5()` builds adjacent compressed extent maps and exercises `btrfs_drop_extent_map_range()` for front split, back split, double split, and whole-map dropping. `valid_ranges[][]` and `validate_range()` assert the exact tree layout after each drop.

`test_case_6()` checks that `btrfs_add_extent_mapping()` does not incorrectly synthesize a gap mapping when two unmerged compressed extent maps sit side by side.

`test_case_7()` is a regression test for `btrfs_drop_extent_map_range(..., skip_pinned=true)`. It ensures a pinned compressed extent is preserved, an unpinned following extent is split correctly, the block start is adjusted, and no unexpected mappings remain.

`test_case_8()` tests compressed extent-map adjustment when adding a large compressed extent that partially overlaps an existing compressed map. It expects the resulting returned map to be trimmed to `[128K, 144K)`, length 16K, with offset 20K.

The reverse-map section defines `struct rmap_test_vector` and `test_rmap_block()`, builds dummy chunk maps/devices, adds them to the mapping tree, and calls `btrfs_rmap_block()` for superblock physical addresses. It validates both a RAID1 chunk that should map to a logical address and an out-of-range single chunk that should not map.

`btrfs_test_extent_map()` uses a 4K dummy fs_info regardless of host page size because its immediate constants assume 4K block size. It allocates a test inode/root, runs all eight extent-map cases, then runs the rmap vectors.
