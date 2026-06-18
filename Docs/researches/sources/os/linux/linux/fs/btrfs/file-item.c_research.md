# File Research: sources/os/linux/linux/fs/btrfs/file-item.c

Btrfs file extent item and checksum implementation. This file provides the low-level helpers that connect file extent B-tree items, in-memory extent maps, inode file-extent presence tracking, and data checksum tree operations used by read, write, logging, truncation, relocation, and extent replacement paths.

Key responsibilities:
- Maintains `inode->disk_i_size` safely with respect to the `NO_HOLES` feature and the in-memory `file_extent_tree`; without `NO_HOLES`, persisted size is limited to the contiguous file-extent-covered range from offset 0.
- Marks or clears inode logical ranges in `inode->file_extent_tree` when file extent items are inserted or removed, enforcing sector alignment except for clear-to-end truncation cases.
- Converts between logical byte counts and packed checksum item byte counts using filesystem sector size and checksum size.
- Inserts explicit regular file extent items representing holes via `btrfs_insert_hole_extent()`.
- Looks up file extent items with `btrfs_lookup_file_extent()`, forwarding caller intent for insertion length and COW/modification.
- Looks up checksums for read bios in `btrfs_lookup_bio_sums()`, including inline checksum storage, heap fallback, csum-tree readahead, free-space-inode commit-root search, and commit-root semaphore protection for past-transaction reads.
- Searches checksum items for arbitrary ranges as either ordered-sum list records (`btrfs_lookup_csums_list()`) or caller-provided checksum buffer plus sector bitmap (`btrfs_lookup_csums_bitmap()`).
- Computes write bio checksums in `btrfs_csum_one_bio()`, either synchronously or through `csum_one_bio_work()`, and attaches `struct btrfs_ordered_sum` to the ordered extent.
- Allocates dummy ordered sums for zoned nodatasum writes so zone append completion can record logical addresses even without checksum bytes.
- Deletes checksum ranges from the checksum tree or log tree through whole-item deletion, batched adjacent-item deletion, middle split, and leading/trailing truncation.
- Inserts ordered-sum checksums into existing or new checksum items, extending adjacent checksum items when possible while respecting max item size, leaf free space, and log-tree next-item boundaries.
- Converts on-disk file extent items into in-memory extent maps for regular, prealloc, explicit hole, compressed, and inline extents.
- Computes the exclusive logical end of a file extent item, rounding inline extents to one sector.

Important data flows:
- `btrfs_lookup_bio_sums()` derives the bio disk range from `bi_iter`, allocates `bbio->csum`, optionally switches to commit-root search, then walks the requested disk range with `search_csum_tree()`. Missing checksums become warnings for normal data but are tolerated for data relocation by marking the inode io tree with `EXTENT_NODATASUM`.
- `btrfs_lookup_csums_list()` searches from the requested start, backs up to a previous overlapping checksum item if needed, then emits one or more `btrfs_ordered_sum` chunks capped by `max_ordered_sum_bytes()`.
- `btrfs_lookup_csums_bitmap()` performs the same checksum-tree walk but copies checksum bytes into a range-relative buffer and sets one bitmap bit per sector covered by a checksum.
- `btrfs_csum_one_bio()` allocates an ordered sum sized for the bio, records the original logical offset and length, attaches it to the ordered extent, and either computes checksum bytes immediately or schedules work that signals `bbio->csum_done`.
- `btrfs_insert_data_csums()` starts at `sums->logical`, repeatedly tries to find or extend an existing checksum item, otherwise inserts a new item sized according to remaining checksums and next checksum item position, then copies checksum bytes until `sums->len` is covered.
- `btrfs_del_csums()` walks backward from the end of the deletion range, which lets it batch-delete covered checksum items and safely handle earlier overlapping items without skipping ranges after mutation.
- `btrfs_extent_item_to_extent_map()` reads the current B-tree path key and item fields, then fills extent-map logical start, length, disk address, disk length, offset, generation, ram bytes, compression flag, prealloc flag, hole marker, or inline marker.

Concurrency and locking:
- `btrfs_inode_safe_disk_i_size_write()` holds `inode->lock` while consulting `file_extent_tree` and updating `disk_i_size`.
- Checksum lookups use B-tree path locking, but commit-root checksum searches set `path->search_commit_root` and `path->skip_locking` while holding `fs_info->commit_root_sem` across multiple searches to avoid mixing checksums from different committed roots.
- Async checksum generation stores the bio iterator in `bbio->csum_saved_iter`, schedules `csum_work`, and completes `bbio->csum_done`.
- Checksum insertion/deletion are transaction-bound B-tree mutations; unrecoverable metadata update failures abort the transaction.
- The bitmap checksum lookup can reuse a caller-supplied B-tree path and leaves path lifecycle to the caller unless it allocated the path internally.

Important invariants:
- Checksum ranges, checksum sizes, and file extent presence ranges are sector/checksum-size aligned.
- A checksum item key offset plus its packed item size defines the logical range covered by the item.
- `btrfs_lookup_csum()` returns `-EFBIG` when the target checksum is exactly at the end of the previous item, signaling an adjacent extension opportunity.
- Missing read checksums are exceptional for normal data roots, but data relocation may copy nodatasum extents whose owning inode flags are not visible on the relocation inode.
- Log-tree checksum insertion must not extend an item across the start offset of a later checksum item already present in the log.
- Inline file extents are represented as `EXTENT_MAP_INLINE`, start at logical offset 0, and get an extent-map length of one sector.
- For old uncompressed regular extents with `ram_bytes < disk_num_bytes`, the extent-map ram bytes are normalized to `disk_num_bytes`.

Notable risks:
- Checksum deletion mutates packed item contents, keys, and item boundaries in several overlap cases; alignment or off-by-one errors can corrupt checksum coverage.
- Commit-root checksum search correctness depends on holding `commit_root_sem` for the whole multi-search walk.
- Checksum insertion optimizes by extending items, but log trees need extra next-offset checks because partial fsyncs can already have overlapping checksum subsets.
- File extent range tracking is used to decide safe persisted i_size without `NO_HOLES`; missed set/clear calls can produce incorrect on-disk size updates.
- `btrfs_extent_item_to_extent_map()` relies on tree-checker invariants for inline extents and only reports unknown extent types as filesystem errors.
