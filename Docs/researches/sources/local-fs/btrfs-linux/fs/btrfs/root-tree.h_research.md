# File Research: sources/local-fs/btrfs-linux/fs/btrfs/root-tree.h

This header declares the root-tree API implemented by `root-tree.c`.

Public interface:
- `btrfs_subvolume_reserve_metadata()` reserves block and qgroup metadata for subvolume/snapshot operations.
- `btrfs_add_root_ref()` and `btrfs_del_root_ref()` create/delete paired root ref and root backref items for subvolume directory references.
- `btrfs_del_root()` deletes a root item by key.
- `btrfs_insert_root()` inserts a new root item.
- `btrfs_update_root()` updates an existing root item, including old-item-size migration.
- `btrfs_find_root()` searches for a root item and optionally returns both decoded item and found key.
- `btrfs_find_orphan_roots()` scans orphan root items at mount/recovery time and queues dead roots.
- `btrfs_set_root_node()` copies extent-buffer root node identity into a root item.
- `btrfs_check_and_init_root_item()` initializes legacy root item flags/limits.
- `btrfs_update_root_times()` updates root ctime and ctransid.

Integration notes:
- The header forward-declares Btrfs transaction, path, root, root item, block reservation, key, fs info, extent buffer, and encrypted-name string structures.
- It is used by transaction, subvolume/snapshot, orphan cleanup, root loading, and relocation code that must manipulate root-tree metadata without depending on the implementation details.
