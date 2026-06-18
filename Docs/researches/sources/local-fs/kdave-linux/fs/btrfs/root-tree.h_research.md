# File Research: sources/local-fs/kdave-linux/fs/btrfs/root-tree.h

## Purpose

`root-tree.h` declares the public interface for Btrfs root-tree operations implemented in `root-tree.c`.

## Declared APIs

- `btrfs_subvolume_reserve_metadata()`: reserve metadata and qgroup accounting for subvolume operations.
- `btrfs_add_root_ref()` / `btrfs_del_root_ref()`: maintain bidirectional root refs/backrefs for subvolume and snapshot directory entries.
- `btrfs_del_root()`: delete a root item from the tree root.
- `btrfs_insert_root()`: insert a new root item.
- `btrfs_update_root()`: update an existing root item, including old-format resizing.
- `btrfs_find_root()`: lookup root items by key, including highest-offset lookup.
- `btrfs_find_orphan_roots()`: scan and queue orphan roots during mount/recovery.
- `btrfs_set_root_node()`: copy extent-buffer node identity into a root item.
- `btrfs_check_and_init_root_item()`: initialize compatibility fields for older root items.
- `btrfs_update_root_times()`: update root ctime and transaction id.

## Dependencies And Integration

The header forward-declares the needed Btrfs and fscrypt types and includes only `<linux/types.h>`. It is used by code that creates, updates, deletes, recovers, or references Btrfs roots, including relocation and snapshot/subvolume paths.

## Risk Notes

The functions declared here mutate core namespace and root metadata. Callers must hold appropriate transaction context and pass root-tree keys that match the intended root item or reference direction.
