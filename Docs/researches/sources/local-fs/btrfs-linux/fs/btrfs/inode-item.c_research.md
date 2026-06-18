# File Research: sources/local-fs/btrfs-linux/fs/btrfs/inode-item.c

## Summary
Implements low-level Btrfs inode item, inode reference, extended inode reference, inode lookup, and inode item truncation helpers. It manipulates packed inode-ref arrays inside B-tree leaves and performs truncation-time deletion or shortening of file extent items with delayed-ref updates.

## Main Responsibilities
- Search normal inode backref items by name.
- Search extended inode backref items by parent objectid and name.
- Lookup, insert, and delete extended inode refs.
- Insert and delete normal inode refs, falling back to extended refs when the normal item overflows.
- Insert empty inode items.
- Lookup inode/root items with special handling for root item searches using offset `-1`.
- Truncate inode-associated B-tree items and file extents according to a `btrfs_truncate_control`.

## Key APIs
- Ref search: `btrfs_find_name_in_backref()`, `btrfs_find_name_in_ext_backref()`, `btrfs_lookup_inode_extref()`.
- Ref mutation: `btrfs_insert_inode_ref()`, `btrfs_del_inode_ref()`.
- Inode item operations: `btrfs_insert_empty_inode()`, `btrfs_lookup_inode()`.
- Truncation: `btrfs_truncate_inode_items()`.

## Important Behavior
Normal inode refs are stored as variable-length `struct btrfs_inode_ref` records packed into one item keyed by child inode and parent objectid. Search loops walk the packed item by each record's name length and compare the fscrypt-aware name bytes in the extent buffer.

Extended inode refs are keyed by `btrfs_extref_hash(parent_objectid, name)` and can contain collision records in one item. Search checks both parent objectid and name. Insert extends an existing item on hash collision unless the same name already exists.

`btrfs_insert_inode_ref()` first attempts the normal inode-ref item. If item insertion or extension overflows and the filesystem has `EXTENDED_IREF`, it inserts an extended ref. If the name already exists, it returns `-EEXIST`; if overflow cannot be represented, it returns `-EMLINK`.

`btrfs_del_inode_ref()` removes a normal ref by deleting the whole item when it contains only that ref, or memmoving later packed refs down and truncating the item. If no matching normal ref exists, it searches and removes the corresponding extended ref.

`btrfs_truncate_inode_items()` walks backward over all keys for an inode at or above `control->min_type`. For file extents, it deletes items fully beyond `new_size`, shrinks regular extent items that straddle `new_size`, truncates simple inline extents when possible, and returns `BTRFS_NEED_TRUNCATE_BLOCK` when an encoded inline extent cannot be safely shortened in place.

When dropping non-inline file extents, truncation clears file extent range state if requested, subtracts inode bytes, queues `BTRFS_DROP_DELAYED_REF` through `btrfs_free_extent()`, and may return `-EAGAIN` to let higher layers refill delayed-ref reservations or end a long transaction.

## State and Synchronization
All mutations require a transaction handle and use Btrfs path COW mode. Packed item changes use extent-buffer memmove, item truncation, and item extension helpers while the path points at the modified leaf.

Truncation batches adjacent pending item deletions to reduce repeated `btrfs_del_items()` calls. For shareable roots it periodically backs off when large amounts of data have been deleted and the transaction should end.

The truncate control structure carries both inputs and outputs: target inode/objectid, minimum key type, whether to skip ref updates, whether to clear in-memory extent ranges, last truncated size, extent count, and bytes to subtract.

## Risks
Packed inode-ref manipulation depends on exact item sizes and name lengths. A wrong `del_len`, memmove range, or collision check can corrupt directory backrefs.

Extended refs are hash keyed, so collision handling is required. Looking only at the key without validating parent objectid and name would delete or find the wrong ref.

Truncation mixes metadata deletion, inline extent resizing, delayed-ref creation, file extent range clearing, inode byte accounting, and transaction throttling. Error handling must abort the transaction on unrecoverable metadata or ref-update failures.

The `skip_ref_updates` flag is powerful and dangerous; it is only correct for callers that already handle extent references elsewhere.
