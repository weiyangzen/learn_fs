# File Research: sources/local-fs/kdave-linux/fs/btrfs/file-item.c

Btrfs file item and checksum implementation. This file owns the low-level helpers for file extent item lookup/conversion, hole extent insertion, inode file-extent presence tracking, checksum lookup for reads, checksum generation for writes, checksum range lookup, checksum insertion, and checksum deletion/truncation in the checksum tree or log tree.

Key responsibilities:
- Maintains `inode->disk_i_size` safely relative to the in-memory file extent presence tree, especially for filesystems without `NO_HOLES`.
- Marks inode logical ranges as having or lacking backing file extent items through `btrfs_inode_set_file_extent_range()` and `btrfs_inode_clear_file_extent_range()`.
- Provides checksum byte-count conversion helpers based on filesystem sector size and checksum size.
- Inserts explicit hole file extents for filesystems that need hole items.
- Looks up file extent items with `btrfs_lookup_file_extent()`, preserving caller control over COW/search modification behavior.
- Looks up read bio checksums with `btrfs_lookup_bio_sums()`, including commit-root searches, free-space inode special handling, missing checksum warnings, and data relocation `NODATASUM` exceptions.
- Searches checksum items for arbitrary ranges and returns either ordered-sum list chunks or a sector bitmap plus checksum buffer.
- Computes write bio checksums synchronously or through workqueue completion, attaching `struct btrfs_ordered_sum` records to ordered extents.
- Allocates dummy ordered sums for zoned nodatasum writes where zone append completion still needs logical address tracking.
- Deletes checksum ranges, including whole-item deletion, item splitting for middle deletions, and edge truncation.
- Inserts checksum data into existing or new checksum items while respecting maximum item sizes, adjacent-item layout, and log-tree overlap constraints.
- Converts on-disk file extent items into in-memory extent maps, including regular, prealloc, hole, compressed, and inline extents.
- Computes the exclusive logical end of a file extent item, rounding inline extents up to sector size.

Important data flows:
- Read checksum lookup starts at `btrfs_lookup_bio_sums()`, allocates inline or heap checksum storage for the bio, optionally pins `commit_root_sem`, then repeatedly calls `search_csum_tree()` until the bio range is covered or a fatal error occurs.
- Write checksum creation starts in `btrfs_csum_one_bio()`, allocates a `btrfs_ordered_sum` sized for the bio, attaches it to the ordered extent, and either calls `csum_one_bio()` immediately or schedules `csum_one_bio_work()`.
- Checksum insertion starts in `btrfs_insert_data_csums()`, tries to locate or extend an adjacent checksum item with `btrfs_lookup_csum()`, otherwise inserts a new item, then copies checksum bytes in chunks until all ordered-sum bytes are persisted.
- Checksum deletion starts from the end of the target range in `btrfs_del_csums()`, walking backward through overlapping items so it can batch-delete covered items and handle partial overlaps without missing earlier checksums.
- File extent conversion uses the current B-tree path key and item body in `btrfs_extent_item_to_extent_map()` to produce the extent-map fields consumed by read, write, fiemap, and seek paths.

Concurrency and locking:
- `btrfs_inode_safe_disk_i_size_write()` takes `inode->lock` while reading the file extent presence tree and updating `disk_i_size`.
- Checksum tree lookups use normal B-tree path locking, but read bio lookup can switch to commit-root searches with `path->skip_locking` while holding `fs_info->commit_root_sem` across repeated searches.
- Checksum generation for async bios stores the bio iterator in `bbio->csum_saved_iter`, schedules work, and signals `bbio->csum_done`.
- Checksum insertion/deletion are transaction-bound and rely on B-tree path write locks, item mutation helpers, and transaction aborts on unrecoverable metadata update failures.

Important invariants:
- Logical checksum ranges and checksum item sizes are sector/checksum-size aligned.
- File extent presence ranges are sector aligned except for the special clear-to-end length `(u64)-1`.
- A checksum item key offset plus item size defines the logical range covered by the packed checksums.
- Missing read checksums are exceptional for normal data roots but can be tolerated for data relocation of nodatasum extents.
- Log-tree checksum insertion must not extend one checksum item across the start of a following checksum item already present in the log tree.
- Inline file extents are represented as `EXTENT_MAP_INLINE`, start at logical offset 0, and have extent-map length equal to one sector.

Notable risks:
- The checksum deletion path mutates packed B-tree item payloads and keys in several overlap cases; off-by-one or alignment mistakes would corrupt checksum coverage.
- Commit-root checksum searches rely on holding `commit_root_sem` across multiple searches to avoid mixing checksums from different transactions.
- `btrfs_insert_data_csums()` optimizes by extending existing items; callers and future changes must preserve the max item and log-tree next-offset rules.
- `btrfs_extent_item_to_extent_map()` trusts tree-checker invariants for inline extents and emits an error only for unknown extent types.
