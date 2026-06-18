# File Research: sources/os/linux/linux/fs/btrfs/inode-item.c

## Purpose
Implements Btrfs inode item, inode reference, extended inode reference, inode lookup, and inode item truncation helpers. In this group, it is directly relevant because `free-space-cache.c` uses `btrfs_truncate_inode_items()` to truncate free-space cache inodes.

## Inode Reference Lookup
- `btrfs_find_name_in_backref()` scans a `BTRFS_INODE_REF_KEY` item for a matching filename.
- `btrfs_find_name_in_ext_backref()` scans a `BTRFS_INODE_EXTREF_KEY` item for matching parent objectid and filename.
- `btrfs_lookup_inode_extref()` computes the extended-ref hash from parent objectid/name and searches for the matching extref item.

## Inode Reference Deletion
- `btrfs_del_inode_extref()` removes one extended inode ref from an item, deleting the entire item if it was the only ref or compacting the item otherwise.
- `btrfs_del_inode_ref()` first tries the regular inode ref item, then falls back to extended inode refs if not found.
- Both return the deleted index through an optional output pointer.

## Inode Reference Insertion
- `btrfs_insert_inode_extref()` inserts or extends an extended inode ref item keyed by CRC32C hash of parent objectid/name.
- `btrfs_insert_inode_ref()` inserts a regular inode ref item, extends an existing item when possible, detects duplicates, and falls back to extended refs on `-EOVERFLOW`/`-EMLINK` if the filesystem has `EXTENDED_IREF`.

## Inode Item Helpers
- `btrfs_insert_empty_inode()` inserts an empty `BTRFS_INODE_ITEM_KEY` item for a given objectid.
- `btrfs_lookup_inode()` searches for an inode/root item and has special handling for root item lookup with offset `-1`, accepting a preceding matching root item.

## Truncation Logic
`btrfs_truncate_inode_items()` removes or shrinks items associated with an inode.

Inputs are provided through `struct btrfs_truncate_control`:
- inode pointer, optional when not clearing extent ranges.
- target `new_size`.
- inode objectid.
- minimum key type to remove.
- flags for skipping reference updates and clearing file extent ranges.

Behavior:
- Scans inode items backwards from max key.
- Removes all item types greater than or equal to `min_type`, subject to offset/new-size rules for `BTRFS_EXTENT_DATA_KEY`.
- For regular/prealloc file extents:
  - Deletes whole extents or shrinks the last overlapping extent.
  - Updates `sub_bytes`, `last_size`, and delayed extent refs through `btrfs_free_extent()`.
- For inline extents:
  - Shrinks unencoded inline extents in place.
  - Returns `BTRFS_NEED_TRUNCATE_BLOCK` when caller must handle an encoded inline tail.
- Batches adjacent item deletions with `btrfs_del_items()`.
- For shareable roots, periodically backs off with `-EAGAIN` when transaction work should end or delayed-ref reservation needs refill.
- Optionally clears file extent ranges from the in-memory inode extent map through `btrfs_inode_clear_file_extent_range()`.

## Error Handling
- Allocation failure returns `-ENOMEM`.
- Missing refs return `-ENOENT`.
- Structural inconsistencies during extref deletion abort the transaction.
- Truncation aborts the transaction on failed extent-range clearing, extent ref drops, or item deletion errors.

## Cross-File Links
- `free-space-cache.c` calls this function with `min_type = BTRFS_EXTENT_DATA_KEY`, `new_size = 0`, and `clear_extent_range = true` to remove data extents from free-space cache inodes.
- The inode creation helper is used by free-space cache inode creation.
