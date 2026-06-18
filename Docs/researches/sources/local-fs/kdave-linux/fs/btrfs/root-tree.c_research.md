# File Research: sources/local-fs/kdave-linux/fs/btrfs/root-tree.c

## Purpose

`root-tree.c` implements root-tree item and root-reference manipulation for Btrfs. The root tree records filesystem roots, snapshots/subvolumes, orphan roots, root refs/backrefs, and root item metadata. This file provides lookup, insert, update, delete, orphan discovery, reference management, root item compatibility initialization, timestamp updates, and metadata reservation for subvolume operations.

## Root Item Reading And Compatibility

`btrfs_read_root_item()` reads a root item from an extent buffer and handles older on-disk root item formats. If the item is smaller than the current structure, or if `generation` and `generation_v2` do not match, it zeroes fields from `generation_v2` onward and generates a fresh UUID. This lets newer kernels mount roots last written by older kernels while detecting partially initialized new fields.

`btrfs_check_and_init_root_item()` handles even older subvolume root items whose `flags` and `byte_limit` fields were not initialized. It uses `BTRFS_INODE_ROOT_ITEM_INIT` in the embedded inode flags as the compatibility marker, then initializes root flags and limit to zero.

## Lookup And Mutation APIs

`btrfs_find_root()` searches a root tree for a `BTRFS_ROOT_ITEM_KEY`. If `search_key->offset` is `-1ULL`, it finds the highest offset for a given root objectid. It returns the root item and/or actual found key when requested, releases the path before returning, and treats an impossible exact `-1ULL` root item as corruption.

`btrfs_set_root_node()` copies a root node extent buffer’s bytenr, level, and generation into a `btrfs_root_item`.

`btrfs_update_root()` finds an existing root item and rewrites it. If the old item is smaller than the current structure, it deletes and reinserts the item at the new size before writing. It updates `generation_v2` to match `generation` before writing, and aborts the transaction if the expected root key is missing or metadata mutation fails.

`btrfs_insert_root()` sets `generation_v2` and inserts a full-size root item.

`btrfs_del_root()` deletes a root item from the tree root, returning `-EUCLEAN` if the key was expected but not found.

## Orphan Root Handling

`btrfs_find_orphan_roots()` scans `BTRFS_ORPHAN_OBJECTID` / `BTRFS_ORPHAN_ITEM_KEY` items in the tree root. For each orphan item:

- If the referenced root no longer exists, it joins a transaction and removes the stale orphan item.
- If the root exists and has zero refs, it checks `drop_progress`.
- Nonzero drop progress marks `BTRFS_FS_UNFINISHED_DROPS` and `BTRFS_ROOT_UNFINISHED_DROP`.
- The root is marked `BTRFS_ROOT_DEAD_TREE` and queued with `btrfs_add_dead_root()`.

This is important for mount-time cleanup and for preventing relocation from running while partially dropped snapshots remain.

## Root Ref And Backref Management

`btrfs_add_root_ref()` inserts both a `BTRFS_ROOT_BACKREF_KEY` and matching `BTRFS_ROOT_REF_KEY`. Each item stores directory id, sequence, name length, and name bytes. Any insertion failure aborts the transaction.

`btrfs_del_root_ref()` deletes both directions. It validates directory id, name length, and name bytes before deleting the backref, returns the stored sequence, then deletes the forward ref. Missing or mismatched items return `-ENOENT`.

These functions keep subvolume/snapshot name references bidirectional in the root tree.

## Timestamps And Reservations

`btrfs_update_root_times()` updates a root item’s ctransid and ctime under `root_item_lock` using real time and the current transaction id.

`btrfs_subvolume_reserve_metadata()` reserves metadata for subvolume create/delete operations. It separately handles qgroup preallocation because subvolume operations affect multiple trees and do not fit normal transaction reservation accounting. It reserves qgroup metadata, reserves block-rsv metadata, optionally falls back to the global block reservation, and records qgroup reservation bytes in the block reservation.

## Dependencies And Integration

This file integrates with:

- tree search/insert/delete helpers from ctree code.
- transaction joining and abort paths.
- disk I/O root loading through `btrfs_get_fs_root()`.
- orphan item deletion and dead-root queues.
- qgroup metadata reservation and release.
- space-info and block reservation accounting.
- root tree consumers such as relocation, snapshots, subvolume creation/deletion, and mount recovery.

## Error Handling And Risks

- Missing expected root items during update/delete are treated as filesystem corruption.
- Root item resizing is transactional and aborts on failure after mutation.
- Root ref deletion validates the user-visible name and directory metadata before deleting to avoid removing the wrong reference.
- Orphan root scanning intentionally marks unfinished drops so relocation can block until cleanup completes.
- Qgroup reservation failures are unwound when block reservation fails.
