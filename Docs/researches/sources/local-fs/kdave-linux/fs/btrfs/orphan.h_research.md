# File Research: sources/local-fs/kdave-linux/fs/btrfs/orphan.h

## Purpose

`orphan.h` declares Btrfs orphan item insertion and deletion helpers.

## Interfaces

Declared functions:

- `btrfs_insert_orphan_item(struct btrfs_trans_handle *trans, struct btrfs_root *root, u64 offset)`
- `btrfs_del_orphan_item(struct btrfs_trans_handle *trans, struct btrfs_root *root, u64 offset)`

## Integration Notes

The header forward-declares transaction and root types and includes only `<linux/types.h>`. It is consumed by cleanup/recovery and metadata mutation code that needs to record or remove orphan items in a root.
