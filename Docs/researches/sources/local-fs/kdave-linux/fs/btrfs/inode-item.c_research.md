# File Research: sources/local-fs/kdave-linux/fs/btrfs/inode-item.c

This file implements Btrfs inode item helpers: inode reference insertion/deletion/lookup, empty inode item insertion, inode lookup, and truncation of inode-associated items and file extents.

Inode reference lookup:
- `btrfs_find_name_in_backref()` scans packed `struct btrfs_inode_ref` records in an inode ref item, matching name length and name bytes.
- `btrfs_find_name_in_ext_backref()` scans packed extended inode refs, matching parent objectid, name length, and name bytes.
- `btrfs_lookup_inode_extref()` computes the extended-ref hash from parent and name, searches for the `BTRFS_INODE_EXTREF_KEY`, and returns the matching extref inside collision-packed records.

Reference deletion:
- `btrfs_del_inode_ref()` first removes a normal `BTRFS_INODE_REF_KEY` subrecord, deleting the whole item if it was the only ref or compacting/truncating the item otherwise.
- If no normal ref/name match is found, it falls back to `btrfs_del_inode_extref()`.
- `btrfs_del_inode_extref()` searches by extref hash, validates the target extref exists, optionally returns its index, and removes or compacts the packed extref item.
- Missing expected extref data during deletion aborts the transaction because it indicates metadata inconsistency.

Reference insertion:
- `btrfs_insert_inode_ref()` inserts or extends a normal inode ref item keyed by child inode objectid and parent objectid.
- Duplicate names return `-EEXIST`.
- If the normal ref item overflows and the `EXTENDED_IREF` incompat feature is enabled, insertion falls back to `btrfs_insert_inode_extref()`.
- `btrfs_insert_inode_extref()` stores refs under a CRC32C hash of parent objectid and name, allowing multiple collision records in one item.
- The caller is expected to enforce `BTRFS_LINK_MAX` before extended-ref insertion.

Inode item helpers:
- `btrfs_insert_empty_inode()` inserts an empty `BTRFS_INODE_ITEM_KEY` item of inode-item size.
- `btrfs_lookup_inode()` wraps `btrfs_search_slot()` and has special handling for root item lookup with offset `-1`, returning the preceding matching root item when appropriate.

Truncation behavior:
- `btrfs_truncate_inode_items()` removes all keys for an inode at or above `control->min_type`, with special handling for file extent items when truncating to `control->new_size`.
- For regular/prealloc file extents, it shrinks a partially retained extent or drops full extents, updates `control->sub_bytes`, clears file extent range state when requested, and queues delayed ref drops through `btrfs_free_extent()`.
- For inline extents, it can shrink unencoded inline data in place; encoded inline extents that cross the new size return `BTRFS_NEED_TRUNCATE_BLOCK` so the caller can handle the final block.
- It batches adjacent item deletions with `btrfs_del_items()` and periodically backs off with `-EAGAIN` for shareable roots when large deletes or delayed-ref reservation pressure appear.
- `skip_ref_updates` lets callers remove file extent items without dropping extent references, and `clear_extent_range` is only valid when an inode is supplied.
- Outputs include number of extents found, last truncated size, and bytes to subtract from inode accounting.

Tracing and diagnostics:
- `btrfs_trace_truncate()` emits tracepoints for inline and regular file extents when an inode is available.
- Transaction aborts are used on failures that indicate metadata update or reference update errors.

Relationship to this group:
- `free-space-cache.c` uses `btrfs_insert_empty_inode()` to create cache inodes and `btrfs_truncate_inode_items()` to clear cache inode extents.
