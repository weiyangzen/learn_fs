# File Research: sources/local-fs/btrfs-linux/fs/btrfs/orphan.c

## Purpose

Provides minimal helpers for inserting and deleting orphan items in a Btrfs root.

## Main Responsibilities

- `btrfs_insert_orphan_item()` inserts an empty item with key `(BTRFS_ORPHAN_OBJECTID, BTRFS_ORPHAN_ITEM_KEY, offset)`.
- `btrfs_del_orphan_item()` searches for the same key and deletes it.

## Key Behaviors

- Both functions allocate a Btrfs path with automatic cleanup.
- Delete returns `-ENOENT` if the orphan item is not found.
- Insert delegates duplicate/error behavior to `btrfs_insert_empty_item()`.
