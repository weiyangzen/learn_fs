# File Research: sources/os/linux/linux/fs/btrfs/orphan.h

This header declares the Btrfs orphan item API.

Exports:
- `btrfs_insert_orphan_item()` inserts an orphan item for a root and object offset in a transaction.
- `btrfs_del_orphan_item()` deletes the corresponding orphan item.

Design notes:
- The header forward declares transaction and root structures, keeping the orphan API small and independent from broader Btrfs internals.
