# File Research: sources/os/linux/linux/fs/xfs/xfs_exchmaps_item.c

Implements log intent/done items and recovery support for exchanging file mappings between two inode forks.

Key behavior:
- Defines XMI intent and XMD done slab caches and log item operations.
- XMI items carry inode numbers, generation numbers, start offsets, blockcount, sizes, and logged exchange flags.
- XMI reference counting handles both log/AIl lifecycle and XMD cancellation.
- XMD done items reference their XMI and are released when committed, dropping the matching intent.
- `xfs_exchmaps_defer_add` submits exchange work to the deferred operation framework.
- Deferred finish calls `xfs_exchmaps_finish_one`; `-EAGAIN` keeps the intent queued for later progress.
- Recovery validates feature support, padding, flags, inode numbers, and file extents; reopens both inodes by handle/generation; estimates resources; recreates incore intent state; and finishes/captures deferred work in recovery transactions.
- Relogging creates a fresh XMI from the old format to move the log tail forward.
- Log recovery pass 2 recreates XMI intent items from log records and releases them when matching XMD records are found.

This file is the transactional crash-recovery layer for multi-step file range exchange operations.
