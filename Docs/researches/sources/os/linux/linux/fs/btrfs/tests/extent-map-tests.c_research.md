# File Research: sources/os/linux/linux/fs/btrfs/tests/extent-map-tests.c

Read completely: 1202 lines.

This file tests extent-map tree insertion, overlap handling, dropping/splitting, compressed extent adjustment, pinned extent behavior, and reverse physical-to-logical mapping.

Shared cleanup:
- `free_extent_map_tree()` removes all mappings from an inode extent-map tree and, in debug builds, reports leaked references.

Extent-map insertion/overlap cases:
- `test_case_1()` simulates concurrent reads where a larger `[0,16K)` map already exists and adding `[0,8K)` should return the existing covering map.
- `test_case_2()` tests repeated inline extent insertion after page-cache discard, expecting the existing inline map.
- `test_case_3()` simulates a buffered write inserting `[4K,8K)` before direct reads add a larger `[0,16K)` map; subcases search before, after, and near the end of the existing map.
- `test_case_4()` simulates direct write splitting `[0,32K)` into `[0,8K)` and `[8K,32K)` while another direct read tries to add the original larger extent.

Drop/split cases:
- `add_compressed_extent()` inserts compressed maps to prevent merging.
- `test_case_5()` creates ranges `[0,12K)`, `[12K,24K)`, `[24K,36K)`, `[36K,40K)`, and `[40K,64K)`, then drops:
  - `[8K,12K)` for front split
  - `[12K,20K)` for back split
  - `[28K,32K)` for double split
  - `[32K,64K)` for whole-map dropping
- `validate_range()` checks the exact tree layout after each drop.

Additional regression cases:
- `test_case_6()` ensures `btrfs_add_extent_mapping()` does not synthesize a bridge extent between two adjacent but unmerged compressed maps.
- `test_case_7()` tests `btrfs_drop_extent_map_range(..., skip_pinned=true)` with a pinned compressed `[0,16K)` map and an unpinned `[32K,48K)` map, ensuring the pinned range survives and the later map is split correctly.
- `test_case_8()` checks compressed map adjustment when an added `[108K,144K)` map overlaps an existing `[120K,128K)` map and the search range is `[140K,144K)`. Expected result is adjusted `[128K,144K)` with offset `20K`.

Reverse mapping:
- `rmap_test_vector` describes chunk layout and expected logical results.
- `test_rmap_block()` builds dummy chunk maps/devices, adds them to the mapping tree, and calls `btrfs_rmap_block()`.
- Cases include a RAID1 chunk intersecting the superblock physical address and a single-profile chunk where the physical address is out of range.

`btrfs_test_extent_map()` creates a dummy 4K fs_info/inode/root, runs cases 1-8, then rmap tests.

Correctness focus:
- Concurrent insertion paths must handle `-EEXIST` by returning useful covering maps.
- Extent-map splitting must preserve logical length, disk bytenr, disk length, offsets, compression flags, and pinned status.
- Compressed extent overlap adjustment is especially sensitive because logical offsets and physical storage lengths differ.
- Reverse mapping must avoid false positives for unrelated physical ranges.
