# File Research: sources/os/linux/linux/fs/btrfs/orphan.c

This file implements simple Btrfs orphan item insertion and deletion helpers.

Core responsibilities:
- Insert a zero-sized orphan item at key `(BTRFS_ORPHAN_OBJECTID, BTRFS_ORPHAN_ITEM_KEY, offset)`.
- Delete the matching orphan item from a root.
- Return `-ENOENT` when deletion is requested for a missing orphan item.

Key mechanisms:
- Both helpers allocate a Btrfs path with `BTRFS_PATH_AUTO_FREE`.
- `btrfs_insert_orphan_item()` calls `btrfs_insert_empty_item()`.
- `btrfs_del_orphan_item()` searches with modification intent and deletes the found item with `btrfs_del_item()`.

Cross-file relationships:
- Public prototypes are in `orphan.h`.
- Used by inode/subvolume orphan cleanup paths to persist objects that need cleanup across crashes or transaction boundaries.
