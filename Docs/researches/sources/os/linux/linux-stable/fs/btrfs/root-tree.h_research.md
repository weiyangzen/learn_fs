# File Research: sources/os/linux/linux-stable/fs/btrfs/root-tree.h

This header declares the root-tree API implemented in `root-tree.c`.

Public API:
- `btrfs_subvolume_reserve_metadata()` reserves metadata and qgroup prealloc space for subvolume operations.
- `btrfs_add_root_ref()` and `btrfs_del_root_ref()` maintain mirrored root reference/backreference items.
- `btrfs_del_root()` deletes a root item.
- `btrfs_insert_root()` inserts a root item.
- `btrfs_update_root()` updates an existing root item.
- `btrfs_find_root()` looks up and decodes a root item.
- `btrfs_find_orphan_roots()` discovers orphan roots during mount/recovery.
- `btrfs_set_root_node()` copies an extent buffer root node location into a root item.
- `btrfs_check_and_init_root_item()` initializes legacy root item fields.
- `btrfs_update_root_times()` updates root timestamp fields during a transaction.

Dependencies and declarations:
- Includes `<linux/types.h>`.
- Forward declares `fscrypt_str`, `extent_buffer`, Btrfs key/root/root item/path/fs info/block reservation, and transaction handle structures.

Role in the subsystem:
- Provides the shared root-tree persistence interface used by subvolume, snapshot, orphan cleanup, relocation, and transaction code without exposing implementation details of root item layout handling.
