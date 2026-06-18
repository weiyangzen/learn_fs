# File Research: sources/os/linux/linux/fs/btrfs/root-tree.c

## Purpose

This file implements root tree item operations for Btrfs roots, root references, orphan roots, root item compatibility repair, root timestamp updates, and metadata reservation for subvolume operations.

The root tree records filesystem roots, snapshots, special trees, root refs/backrefs, and orphan/dead roots. Relocation uses these helpers to create, update, find, and delete relocation root items.

## Root Item Reading and Compatibility

`btrfs_read_root_item()`:
- Reads a `struct btrfs_root_item` from a leaf.
- Supports older on-disk root items smaller than the current struct.
- Detects mismatched `generation` and `generation_v2`, which indicates the root may have been mounted by an older kernel.
- Clears newer fields from `generation_v2` onward and generates a new UUID when reset is needed.

`btrfs_check_and_init_root_item()`:
- Works around old kernels that did not initialize `root_item->flags` and `root_item->byte_limit`.
- Uses `BTRFS_INODE_ROOT_ITEM_INIT` in the embedded inode flags to detect initialization.
- Initializes root flags and byte limit to zero if needed.

## Root Lookup and Mutation

`btrfs_find_root()`:
- Searches the root tree for a root item key.
- If the search offset is `-1ULL`, finds the highest offset for the objectid.
- Returns the root item and/or exact found key to the caller.
- Rejects an exact impossible `offset == -1ULL` match as corruption.
- Releases the path before returning.

`btrfs_set_root_node()`:
- Copies an extent buffer’s bytenr, level, and generation into a root item.

`btrfs_update_root()`:
- Searches for an existing root item and overwrites it.
- If the on-disk item is smaller than the current root item, deletes and reinserts it with the full size.
- Updates `generation_v2` to match `generation`.
- Aborts the transaction if the expected root key is missing or reinsertion fails.

`btrfs_insert_root()`:
- Sets `generation_v2` and inserts a new root item.

`btrfs_del_root()`:
- Deletes a root item by key.
- Treats a missing expected root item as `-EUCLEAN`.

## Orphan Root Handling

`btrfs_find_orphan_roots()`:
- Scans `BTRFS_ORPHAN_OBJECTID` / `BTRFS_ORPHAN_ITEM_KEY` entries in the root tree.
- Looks up each referenced root.
- If the root no longer exists, joins a transaction and deletes the stale orphan item.
- If the root has zero refs, marks it as a dead tree and queues it for deletion.
- If `drop_progress` is nonzero, marks filesystem/root state so unfinished snapshot drops block balance/relocation until cleanup completes.

This directly protects relocation because `btrfs_relocate_block_group()` waits on `BTRFS_FS_UNFINISHED_DROPS` before starting.

## Root References

Btrfs stores both forward and backward root references. This file keeps them paired.

`btrfs_add_root_ref()`:
- Inserts a `BTRFS_ROOT_BACKREF_KEY` item and then a matching `BTRFS_ROOT_REF_KEY` item.
- Stores directory id, sequence number, name length, and name bytes in each root ref item.
- Aborts the transaction on insertion failure.

`btrfs_del_root_ref()`:
- Deletes the backref item first, verifying dirid and name match.
- Returns the removed sequence through the caller pointer.
- Then deletes the matching forward ref item.
- Returns `-ENOENT` for mismatched/missing references.

## Root Timestamps

`btrfs_update_root_times()`:
- Gets current real time.
- Updates root change transaction id and ctime under `root_item_lock`.

## Subvolume Metadata Reservation

`btrfs_subvolume_reserve_metadata()`:
- Reserves metadata for subvolume creation/deletion style operations.
- If qgroups are enabled, reserves qgroup metadata first.
- Calculates insert metadata size from the requested item count.
- Uses the metadata space info and temporary block reservation.
- Can fall back to the global block reservation when requested.
- On success, accounts qgroup preallocation bytes in the reservation.
- On failure, frees qgroup preallocation.

## Dependencies

This file depends on:
- Root tree B-tree search/insert/delete primitives.
- Extent buffer accessors.
- Transaction management.
- Qgroup metadata reservation.
- Orphan root deletion logic.
- Space info and block reservation helpers.
- UUID generation for compatibility reset.

## Risk Notes

Root tree operations are core metadata operations. Important risks include failing to keep forward/backward root refs paired, mishandling older root item sizes, losing orphan root cleanup state, and updating root items without synchronizing `generation_v2`. These paths are also important to relocation because relocation roots are inserted, updated, found, and deleted through this API.
