# File Research: sources/local-fs/btrfs-linux/fs/btrfs/root-tree.c

This file implements root-tree item lookup, insertion, update, deletion, root reference/backreference items, orphan-root discovery, root-item compatibility initialization, root timestamp updates, and metadata reservation for subvolume operations.

Root item compatibility:
- `btrfs_read_root_item()` reads a root item from a leaf and handles old on-disk root item sizes.
- If the item is shorter than the current structure, or `generation` and `generation_v2` disagree, fields from `generation_v2` onward are cleared and a new random UUID is generated.
- This preserves mount compatibility for roots last written by older kernels that did not know newer root-item fields.
- `btrfs_check_and_init_root_item()` handles older subvolumes that did not initialize `root_item->flags` and `root_item->byte_limit`, using `BTRFS_INODE_ROOT_ITEM_INIT` in the embedded inode flags as the migration marker.

Root item operations:
- `btrfs_find_root()` searches the root tree for a `BTRFS_ROOT_ITEM_KEY`. If the search key offset is `-1ULL`, it finds the highest offset for the objectid. It can return the decoded `btrfs_root_item` and the actual found key.
- `btrfs_set_root_node()` copies a root node extent buffer’s bytenr, level, and generation into a root item.
- `btrfs_update_root()` searches for an existing root item, enlarges old short items by deleting/reinserting them when needed, synchronizes `generation_v2`, and writes the full root item back to the tree.
- `btrfs_insert_root()` inserts a new root item and sets `generation_v2` to match `generation`.
- `btrfs_del_root()` deletes an exact root item from the tree root and treats a missing expected key as filesystem corruption (`-EUCLEAN`).

Orphan root recovery:
- `btrfs_find_orphan_roots()` scans `BTRFS_ORPHAN_OBJECTID/BTRFS_ORPHAN_ITEM_KEY` items in the tree root.
- If an orphan item points to a missing root, it joins a transaction and deletes the stale orphan item.
- If the root exists and has zero refs, it marks the root as dead, adds it to dead-root cleanup, and detects nonzero `drop_progress`.
- Roots with nonzero drop progress set `BTRFS_FS_UNFINISHED_DROPS` and `BTRFS_ROOT_UNFINISHED_DROP`, which blocks relocation until incomplete snapshot deletion is finished.

Root reference operations:
- `btrfs_add_root_ref()` inserts both the backref (`BTRFS_ROOT_BACKREF_KEY`) and forward ref (`BTRFS_ROOT_REF_KEY`) items, storing parent dirid, sequence, name length, and name bytes.
- `btrfs_del_root_ref()` deletes the matching backref and forward ref, validating dirid, name length, and name bytes, and returns the stored sequence to the caller.
- These functions encode the subvolume/snapshot directory relationship in both lookup directions.

Timestamps and reservation:
- `btrfs_update_root_times()` updates root ctransid and ctime under `root_item_lock` using current real time.
- `btrfs_subvolume_reserve_metadata()` reserves metadata for subvolume/snapshot create/delete style operations that touch multiple roots and the root tree.
- When qgroups are enabled, it pre-reserves qgroup metadata for the parent inode and directory entries, then reserves block-rsv metadata with full flushing and optionally migrates from the global reserve.
- On failure it releases qgroup preallocation; on success it records the qgroup reservation in the supplied block reservation.

Error handling:
- Missing mandatory root items and failed root-ref insertions abort the current transaction where appropriate.
- Root lookup releases paths before returning in all normal cases.
- Orphan cleanup logs failures to join transactions or delete stale orphan items.
