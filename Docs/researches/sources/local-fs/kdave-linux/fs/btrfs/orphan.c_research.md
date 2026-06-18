# File Research: sources/local-fs/kdave-linux/fs/btrfs/orphan.c

## Purpose

`orphan.c` provides small helpers to insert and delete orphan items in a Btrfs root tree.

## Behavior

`btrfs_insert_orphan_item()` builds a key with:

- `objectid = BTRFS_ORPHAN_OBJECTID`
- `type = BTRFS_ORPHAN_ITEM_KEY`
- `offset = caller-supplied offset`

It allocates a path and inserts an empty item with zero payload into the given root.

`btrfs_del_orphan_item()` builds the same key, searches for it with a deletion intent, returns `-ENOENT` if missing, and calls `btrfs_del_item()` if found.

Both functions use `BTRFS_PATH_AUTO_FREE(path)` for cleanup and return `-ENOMEM` on path allocation failure.

## Dependencies and Integration

The file depends on `ctree.h` and `orphan.h`. Orphan items are used by higher-level inode/subvolume cleanup paths to record objects requiring cleanup across transaction boundaries or mount recovery.

## Risk Notes

The helper is intentionally thin. Correctness is delegated to transaction callers and B-tree insertion/deletion primitives.
