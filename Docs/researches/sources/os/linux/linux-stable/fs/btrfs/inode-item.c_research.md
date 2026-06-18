# File Research: sources/os/linux/linux-stable/fs/btrfs/inode-item.c

## Purpose

Implements helpers for Btrfs inode item lookup/creation, inode reference insertion/removal, extended inode references, and inode item truncation. In this group it matters because free-space cache v1 uses `btrfs_insert_empty_inode()` to create cache inodes and `btrfs_truncate_inode_items()` to truncate cache inode extents.

## Inode Reference Helpers

`btrfs_find_name_in_backref()` scans packed `BTRFS_INODE_REF_KEY` subrecords in an item and matches by name. `btrfs_find_name_in_ext_backref()` scans `BTRFS_INODE_EXTREF_KEY` records and matches by parent objectid plus name. `btrfs_lookup_inode_extref()` searches the hashed extended-ref key and returns the matching extref record if present.

`btrfs_insert_inode_ref()` inserts a normal inode ref, extends an existing packed item if needed, detects duplicate names, and falls back to `btrfs_insert_inode_extref()` when the normal item overflows and the `EXTENDED_IREF` incompat feature is enabled. `btrfs_del_inode_ref()` removes a normal ref by compacting or deleting the item and falls back to `btrfs_del_inode_extref()` if the normal ref is missing.

## Inode Item Helpers

`btrfs_insert_empty_inode()` inserts an empty `BTRFS_INODE_ITEM_KEY` for a given objectid. `btrfs_lookup_inode()` searches for an inode/root item and includes special handling for root-item lookups with offset `-1`, where the preceding matching root item may satisfy the lookup.

## Truncation Algorithm

`btrfs_truncate_inode_items()` removes all items for an inode at or above `control->min_type`, and for file extents removes or shrinks extents at/after `control->new_size`. It walks backward from the highest key for the inode, batches adjacent deletions, updates `control->last_size`, `control->sub_bytes`, and `control->extents_found`, and can return `BTRFS_NEED_TRUNCATE_BLOCK` for inline extents that cannot be partially truncated due to compression/encryption/encoding.

For regular extents it may shrink the extent item, clear in-memory file extent ranges when requested, and drop delayed extent refs with `btrfs_free_extent()` unless `skip_ref_updates` is set. For shareable roots it periodically backs off with `-EAGAIN` when transactions should end or delayed-ref reservations need refill.

## Error Handling And Transactions

Most modifying paths use COW-capable `btrfs_search_slot()` and abort the transaction on unexpected metadata inconsistency or delayed-ref/free-extent errors. Path allocation failure returns `-ENOMEM`; missing refs generally return `-ENOENT`; normal-ref overflow can become `-EMLINK` or extended-ref insertion.

## Integration Notes

This file depends on ctree/search primitives, extent-buffer accessors, transactions, delayed refs, extent-tree freeing, file extent accessors, and tracing. The free-space cache truncate path constructs a `btrfs_truncate_control` with `min_type = BTRFS_EXTENT_DATA_KEY`, `new_size = 0`, and `clear_extent_range = true` to remove cache inode file extents safely.
