# File Research: sources/os/linux/linux-stable/fs/btrfs/tests/extent-map-tests.c

## Role
Regression and behavior tests for the in-memory extent-map tree and physical-to-logical reverse mapping.

## Main Helpers
- `free_extent_map_tree` removes and frees all extent maps from an inode and, under debug builds, checks for leaked references.
- `add_compressed_extent` inserts compressed extent maps that intentionally do not merge with neighbors.
- `validate_range` checks the exact extent-map tree layout against expected ranges after drop operations.
- `test_rmap_block` creates a dummy chunk map with dummy devices, inserts it into the mapping tree, calls `btrfs_rmap_block`, and validates mapped logical addresses and stripe length.

## Test Cases
- `test_case_1` simulates concurrent reads where a smaller add overlaps an already loaded larger extent and should return the existing `[0, 16K)` map.
- `test_case_2` covers repeated inline extent insertion after page-cache discard and expects the existing inline extent map to be returned.
- `test_case_3` covers a buffered-write map inside a larger file extent while concurrent reads add neighboring portions of the same original extent.
- `test_case_4` covers direct-write splitting of `[0, 32K)` into `[0, 8K)` and `[8K, 32K)` while concurrent reads add ranges from the original extent.
- `test_case_5` exercises `btrfs_drop_extent_map_range` front split, back split, double split, and whole-map dropping across compressed extents.
- `test_case_6` verifies `btrfs_add_extent_mapping` does not incorrectly synthesize a bridging map between two adjacent unmerged extents.
- `test_case_7` is a pinned-extent regression test for `btrfs_drop_extent_map_range(..., skip_pinned=true)`, checking that pinned extents are preserved and following extents are split with correct logical and block starts.
- `test_case_8` verifies compressed extent-map adjustment when a newly added compressed map partially overlaps an existing compressed map; the result must adjust start, length, and offset.
- The rmap vectors check a RAID1 chunk whose physical stripe intersects the superblock physical address and a single-stripe out-of-range physical address that should not map.

## Entry Point
`btrfs_test_extent_map` allocates 4 KiB dummy fs_info, a test inode, and a dummy root, runs cases 1-8, then runs the rmap vectors.

## Dependencies
Depends on Btrfs inode extent-map trees, chunk maps and mapping tree operations, dummy devices, block group constants, compressed extent flags, and reverse mapping logic.
