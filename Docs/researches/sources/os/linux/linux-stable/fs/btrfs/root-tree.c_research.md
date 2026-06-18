# File Research: sources/os/linux/linux-stable/fs/btrfs/root-tree.c

This file implements root-tree item lookup, insertion, update, deletion, root reference maintenance, orphan-root discovery, root item compatibility initialization, root timestamp updates, and metadata reservation for subvolume operations.

Root item compatibility:
- `btrfs_read_root_item()` reads an on-disk root item into memory and supports older, shorter root-item formats. If the item is shorter than the current structure, or `generation` and `generation_v2` mismatch, it zeros fields from `generation_v2` onward and generates a fresh UUID.
- `btrfs_check_and_init_root_item()` handles older subvolume root items that did not initialize `flags` and `byte_limit`, using `BTRFS_INODE_ROOT_ITEM_INIT` in the embedded inode flags as the initialization marker.

Root lookup and mutation:
- `btrfs_find_root()` searches the root tree for a `BTRFS_ROOT_ITEM_KEY`. When the search key offset is `-1ULL`, it returns the highest-offset root item for the given objectid. It optionally returns both the decoded root item and the actual found key.
- `btrfs_set_root_node()` copies an extent buffer's bytenr, level, and generation into a root item.
- `btrfs_update_root()` searches for an existing root item, aborts the transaction on missing/corrupt state, expands older short items to the current root item size when needed, updates `generation_v2`, and writes the full root item.
- `btrfs_insert_root()` initializes `generation_v2` and inserts a new root item into the root tree.
- `btrfs_del_root()` deletes a root item by exact key and returns `-EUCLEAN` if the expected item is missing.

Orphan root handling:
- `btrfs_find_orphan_roots()` scans `BTRFS_ORPHAN_ITEM_KEY` items in the tree root. For each orphan item, it loads the referenced root, removes stale orphan items whose roots no longer exist, marks roots with zero refs as dead, queues them on the dead-root list, and sets unfinished-drop flags when `drop_progress` is non-zero.
- This unfinished-drop state is relevant to relocation because `btrfs_relocate_block_group()` waits for `BTRFS_FS_UNFINISHED_DROPS` before relocating, and `create_reloc_root()` rejects partially dropped subvolumes.

Root references:
- `btrfs_add_root_ref()` inserts both `BTRFS_ROOT_BACKREF_KEY` and `BTRFS_ROOT_REF_KEY` items for a subvolume/snapshot reference, storing directory id, sequence, name length, and name bytes.
- `btrfs_del_root_ref()` removes the mirrored backref and forward ref, validates dirid/name on the backref item, and returns the recorded sequence.

Root metadata and timestamps:
- `btrfs_update_root_times()` updates root creation transaction id and ctime/nsec fields under `root_item_lock`.
- `btrfs_subvolume_reserve_metadata()` reserves metadata for subvolume and snapshot creation/deletion. It reserves qgroup metadata prealloc bytes when qgroups are enabled, reserves normal metadata bytes from the block reservation, can fall back to the global reservation, and records qgroup reservation bytes in the reservation.

Important dependencies:
- Root-tree operations use Btrfs path/search/item helpers from `ctree.h`, transactions from `transaction.h`, root reading from `disk-io.h`, qgroup reservation helpers from `qgroup.h`, space-info lookup, and orphan item deletion from `orphan.h`.
- Random UUID generation is used only for compatibility reset of old root items.

Error handling and invariants:
- Missing root items during update or deletion are treated as corruption (`-EUCLEAN`) rather than benign absence.
- `btrfs_update_root()` aborts the transaction when root item lookup, deletion, or reinsertion fails after it has entered a mutating path.
- Root reference insertion aborts the transaction if either mirrored item cannot be inserted.
- `btrfs_find_orphan_roots()` releases the search path before loading roots or deleting stale orphan items, avoiding holding tree locks across those operations.

Role in the subsystem:
- This file is the root-tree persistence layer for subvolumes, snapshots, relocation roots, orphan cleanup, and root reference metadata. `relocation.c` relies on it to create, update, delete, and recover relocation root items.
