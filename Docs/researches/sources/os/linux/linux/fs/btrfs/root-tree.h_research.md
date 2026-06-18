# File Research: sources/os/linux/linux/fs/btrfs/root-tree.h

## Purpose

This header declares Btrfs root tree helper APIs for root item lookup/mutation, root references, orphan root discovery, root item initialization, root timestamps, and subvolume metadata reservation.

## Declared APIs

Root item operations:
- `btrfs_find_root()`
- `btrfs_insert_root()`
- `btrfs_update_root()`
- `btrfs_del_root()`
- `btrfs_set_root_node()`

Root reference operations:
- `btrfs_add_root_ref()`
- `btrfs_del_root_ref()`

Root lifecycle and compatibility:
- `btrfs_find_orphan_roots()`
- `btrfs_check_and_init_root_item()`
- `btrfs_update_root_times()`

Reservation:
- `btrfs_subvolume_reserve_metadata()`

## Integration Role

The header is consumed by Btrfs modules that need to manipulate root tree records without knowing root-tree implementation details. In this group, `relocation.c` uses `btrfs_insert_root()`, `btrfs_update_root()`, and related root-tree semantics when creating, persisting, recovering, and deleting relocation roots.

## Risk Notes

The API surface is small but metadata-critical. Callers must pass transaction handles and keys that match real root-tree state; missing root items or mismatched root refs are treated as corruption or transaction-aborting errors by the implementation.
