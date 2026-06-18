# File Research: sources/local-fs/btrfs-linux/fs/btrfs/file-item.c

## Purpose

Implements Btrfs file extent item helpers and checksum-tree operations. This file bridges on-disk file extent metadata, in-memory extent maps, ordered write checksums, read bio checksum lookup, checksum insertion/deletion, and inode disk-size safety tracking.

## Main Responsibilities

- Maintains `disk_i_size` safely relative to real file extents when hole extent items are required.
- Tracks file extent coverage in an inode-local extent state tree through `EXTENT_DIRTY`.
- Inserts explicit hole file extent items.
- Searches file extent items by inode/objectid and file offset.
- Looks up checksums for read bios, checksum ranges, and bitmap-based checksum requests.
- Calculates checksums for write bios, synchronously or via workqueue.
- Allocates dummy ordered sums for zoned nodatasum writes where Zone Append completion updates logical addresses.
- Deletes checksum items over byte ranges, including truncating or splitting partially overlapped checksum items.
- Inserts ordered checksums into the checksum tree, extending adjacent checksum items where possible.
- Converts on-disk `btrfs_file_extent_item` records into `struct extent_map`.
- Computes the logical end offset of a file extent item.

## Important APIs

- `btrfs_inode_safe_disk_i_size_write()` sets `disk_i_size` to the safe contiguous byte range from file offset 0, or directly to `i_size` when the inode has no file-extent tracking tree.
- `btrfs_inode_set_file_extent_range()` and `btrfs_inode_clear_file_extent_range()` update inode file-extent coverage bits after inserting or removing file extent items.
- `btrfs_insert_hole_extent()` creates a regular file extent item with `disk_bytenr == 0`, representing an explicit hole.
- `btrfs_lookup_file_extent()` wraps `btrfs_search_slot()` for `BTRFS_EXTENT_DATA_KEY` lookup.
- `btrfs_lookup_bio_sums()` allocates and fills `bbio->csum` for read verification.
- `btrfs_lookup_csums_list()` returns found checksums as `btrfs_ordered_sum` list entries.
- `btrfs_lookup_csums_bitmap()` fills a checksum buffer and sector bitmap for found checksums.
- `btrfs_csum_one_bio()` creates an ordered checksum record and calculates sector checksums for a write bio.
- `btrfs_alloc_dummy_sum()` attaches an empty ordered sum for zoned nodatasum IO.
- `btrfs_del_csums()` removes checksum records for a byte range.
- `btrfs_insert_data_csums()` writes ordered sums into the checksum or log tree.
- `btrfs_extent_item_to_extent_map()` initializes extent-map fields from regular, prealloc, hole, compressed, and inline file extent items.
- `btrfs_file_extent_end()` returns the non-inclusive logical end of the file extent item at a path slot.

## Control Flow

Checksum lookup centers on `search_csum_tree()`, which reuses the current path when possible and otherwise searches the appropriate checksum root for the target logical bytenr. `btrfs_lookup_bio_sums()` walks a read bio sector range, fills checksum slots, uses commit-root searches for free-space inodes and optionally for past-transaction reads, and handles checksum holes by warning or marking data-relocation sectors as nodatasum.

Checksum range lookups first search at `start`, then step back to the previous checksum item if it overlaps the range. They then iterate forward through checksum items, clipping to the requested range. The list variant allocates bounded `btrfs_ordered_sum` chunks; the bitmap variant copies into caller-owned storage and sets one bit per covered sector.

Checksum deletion scans backward from the end of the target range. Fully covered checksum items are batch-deleted. Leading or trailing overlaps are handled by `truncate_one_csum()`. Middle overlaps are split in place by zeroing the dropped checksum bytes and using `btrfs_split_item()` so the next loop can delete/truncate a cleanly bounded item.

Checksum insertion tries to locate an existing checksum item ending at the insertion point and extend it, subject to leaf space and `MAX_CSUM_ITEMS`. For log trees, it avoids extending across the next checksum item because the log can contain partial overlapping checksum history from repeated fsyncs. If extension is not suitable, it inserts a new checksum item sized to fit the remaining ordered sum and the next checksum item boundary.

Extent-map conversion distinguishes regular/prealloc extents, explicit holes (`disk_bytenr == 0`), compressed extents, and inline extents. For old non-compressed extents with `ram_bytes < disk_num_bytes`, it normalizes `ram_bytes` to `disk_num_bytes`.

## Dependencies

This file depends on Btrfs btree path/search/mutation helpers, checksum roots, ordered extents, bio wrappers, compression flags, extent maps, transaction handles, file extent item accessors, and filesystem geometry such as `sectorsize`, `sectorsize_bits`, `csum_size`, and `csums_per_leaf`.

## Invariants And Risks

- Checksum and file-extent operations assume sectorsize alignment; assertions enforce this in conversion helpers and range tracking.
- `btrfs_lookup_bio_sums()` must not mix checksum data from different commit roots when `csum_search_commit_root` is set, so it holds `commit_root_sem` across repeated searches.
- Checksum item splitting/truncation mutates btree items in place and must preserve key offsets exactly.
- Log-tree checksum insertion has stricter overlap constraints than the main checksum tree.
- Missing checksums for non-nodatasum reads are suspicious except in data relocation of nodatasum extents.
- `btrfs_extent_item_to_extent_map()` trusts tree-checker guarantees for inline extents starting at file offset 0.
