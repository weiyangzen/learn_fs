# File Research: sources/os/linux/linux-stable/fs/btrfs/orphan.c

## Summary
Implements insertion and deletion of Btrfs orphan items in a root.

## Main Responsibilities
- Inserts empty orphan items keyed by orphan objectid and caller-provided offset.
- Deletes existing orphan items by searching and removing the item from the tree.

## Key APIs
- `btrfs_insert_orphan_item()`.
- `btrfs_del_orphan_item()`.

## Important Behavior
Both functions build a key with `objectid = BTRFS_ORPHAN_OBJECTID`, `type = BTRFS_ORPHAN_ITEM_KEY`, and `offset = offset`.

Insertion allocates a path and calls `btrfs_insert_empty_item()` with zero item size.

Deletion searches with modification intent, returns search errors directly, returns `-ENOENT` if the item is absent, and calls `btrfs_del_item()` when found.

## State and Synchronization
The caller supplies the active transaction and root. Path lifetime is handled with `BTRFS_PATH_AUTO_FREE`.

## Risks
The helpers are intentionally thin. Correctness depends on callers choosing the right root/offset and holding a transaction appropriate for modifying the root tree.
