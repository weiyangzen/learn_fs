# File Research: sources/os/linux/linux-stable/fs/btrfs/file-item.c

Btrfs file extent item and checksum implementation. This file connects on-disk file extent items, in-memory extent maps, inode file-extent range tracking, ordered write checksums, read-bio checksum lookup, and checksum tree mutation.

Key responsibilities:
- Maintains `inode->disk_i_size` safely. With `NO_HOLES`, it can mirror `i_size`; without it, the safe disk size is limited to the contiguous file-extent-covered range starting at offset 0.
- Tracks logical file extent coverage in `inode->file_extent_tree` when extent items are inserted or removed.
- Inserts explicit hole extents with `btrfs_insert_hole_extent()`.
- Looks up file extent items through `btrfs_lookup_file_extent()`.
- Looks up read-bio checksums in `btrfs_lookup_bio_sums()`, including inline checksum storage, heap fallback, checksum-tree readahead, free-space-inode commit-root search, and commit-root semaphore protection for past-transaction reads.
- Provides list and bitmap checksum range lookup through `btrfs_lookup_csums_list()` and `btrfs_lookup_csums_bitmap()`.
- Computes write bio checksums in `btrfs_csum_one_bio()`, synchronously or with async work, and attaches `btrfs_ordered_sum` records to ordered extents.
- Allocates dummy ordered sums for zoned nodatasum writes so zone append completion can still record logical addresses.
- Deletes checksum ranges with whole-item deletion, batched deletion, leading/trailing truncation, or middle splitting.
- Inserts ordered checksum records into checksum/log trees, extending adjacent checksum items when possible while respecting item size, leaf space, and log-tree overlap constraints.
- Converts on-disk `btrfs_file_extent_item` records into `struct extent_map` entries for regular, prealloc, explicit hole, compressed, and inline extents.
- Computes the exclusive logical end of a file extent item with inline extents rounded to sector size.

Important data flows:
- `btrfs_lookup_bio_sums()` derives the disk range from `bio->bi_iter`, allocates `bbio->csum`, then repeatedly calls `search_csum_tree()` to fill sector checksums. Missing checksums warn for normal data, but for data relocation they mark the inode io tree with `EXTENT_NODATASUM`.
- `btrfs_lookup_csums_list()` searches at the requested start, backs up to a previous overlapping checksum item if needed, and emits bounded `btrfs_ordered_sum` chunks.
- `btrfs_lookup_csums_bitmap()` performs a similar walk but copies checksum bytes into a caller buffer and sets one bitmap bit per sector with a checksum.
- `btrfs_del_csums()` walks backward from the deletion range end so item deletion/truncation does not skip earlier overlapping checksum items.
- `btrfs_insert_data_csums()` starts at `sums->logical`, finds or extends an item when possible, otherwise inserts a new item sized by remaining checksum count and next checksum item position.
- `btrfs_extent_item_to_extent_map()` reads the current path key and item fields, then fills extent-map logical range, disk range, offset, generation, ram bytes, compression/prealloc flags, hole marker, or inline marker.

Concurrency and invariants:
- `btrfs_inode_safe_disk_i_size_write()` holds `inode->lock` while reading file extent tracking and updating `disk_i_size`.
- Commit-root checksum searches set `path->search_commit_root` and `path->skip_locking`, and hold `fs_info->commit_root_sem` across repeated searches to avoid mixing committed roots.
- Checksum and file extent coverage ranges are sector-size aligned; checksum byte counts are checksum-size aligned.
- `btrfs_lookup_csum()` returns `-EFBIG` when the requested checksum is exactly adjacent to the previous item, signaling an extension opportunity.
- Missing read checksums are exceptional for normal data roots but tolerated for data relocation of nodatasum extents.
- Log-tree checksum insertion must not extend a checksum item across a later checksum item already present in the log.
- Inline file extents are represented as `EXTENT_MAP_INLINE`, start at logical offset 0, and map to one sector in the extent map.

Notable risks:
- Checksum item deletion mutates packed item contents, keys, and item boundaries in several overlap cases; off-by-one or alignment mistakes can corrupt checksum coverage.
- Commit-root lookup correctness depends on holding `commit_root_sem` for the whole multi-search walk.
- File extent range tracking feeds safe `disk_i_size`; missed set/clear calls can produce unsafe persisted sizes on filesystems without `NO_HOLES`.
- `btrfs_extent_item_to_extent_map()` relies on tree-checker invariants for inline extents and only reports unknown extent types as filesystem errors.
