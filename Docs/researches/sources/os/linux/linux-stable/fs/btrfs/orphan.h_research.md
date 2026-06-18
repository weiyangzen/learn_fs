# File Research: sources/os/linux/linux-stable/fs/btrfs/orphan.h

## Summary
Declares Btrfs orphan item insertion and deletion helpers.

## Main Contents
- Forward declarations for `struct btrfs_trans_handle` and `struct btrfs_root`.
- `btrfs_insert_orphan_item()`.
- `btrfs_del_orphan_item()`.

## Risks
The header exposes only transaction-root-offset operations. Callers must enforce orphan lifecycle policy outside this file.
