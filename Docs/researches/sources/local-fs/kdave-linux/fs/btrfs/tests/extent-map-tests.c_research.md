# File Research: sources/local-fs/kdave-linux/fs/btrfs/tests/extent-map-tests.c

This file tests the inode extent-map tree, especially concurrent-style `btrfs_add_extent_mapping()` EEXIST handling, range dropping/splitting, pinned/compressed map regressions, and reverse mapping from physical to logical addresses.

`free_extent_map_tree()` removes and frees all extent maps from an inode, with debug refcount validation under `CONFIG_BTRFS_DEBUG`.

Test cases 1 through 4 simulate races where one path has already inserted a larger or split extent map and a second path attempts to add an overlapping map. They validate that the existing or adjusted map returned covers the requested range correctly for normal, inline, buffered-write, and direct-write split scenarios.

`test_case_5()` creates compressed maps over adjacent file ranges and then drops front, back, middle, and whole ranges using `btrfs_drop_extent_map_range()`. It validates the exact remaining extent map tree after each drop.

`test_case_6()` validates that `btrfs_add_extent_mapping()` does not incorrectly synthesize a gap map between two adjacent but intentionally unmerged compressed extents.

`test_case_7()` is a pinned-map regression test. It drops a range with `skip_pinned` true and checks that a pinned compressed map remains intact while a later non-pinned map is split with correct start, length, and block start.

`test_case_8()` validates compressed extent-map adjustment when inserting a larger compressed map partially overlapped by an existing map. Expected result is an adjusted `[128K, 144K)` map with length 16K and offset 20K.

Reverse mapping tests construct dummy chunk maps and devices, call `btrfs_rmap_block()`, and validate whether physical superblock addresses map to expected logical addresses and stripe length.

`btrfs_test_extent_map()` allocates a dummy 4K filesystem/inode/root, runs all extent-map cases, then runs rmap vectors before cleanup.
