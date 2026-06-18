# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_log_recover.h

This header declares internal log recovery structures, item-operation callbacks, transaction reconstruction data, and helper APIs for replay.

Key contents:
- `enum xlog_recover_reorder`, controlling recovered item ordering into buffer, item, inode-buffer, and cancel lists.
- `struct xlog_recover_item_ops`, the per-log-item recovery vtable:
  - item type
  - reorder callback
  - pass2 readahead callback
  - pass1 commit callback
  - pass2 commit/replay callback
- Extern declarations for all supported recovery item ops, including realtime intent variants.
- Recovery hash constants for transaction IDs.
- `struct xlog_recover_item`, storing recovered log item regions and decoded ops.
- `struct xlog_recover`, representing a partially reconstructed transaction.
- Recovery pass constants: CRC pass, pass1, pass2.
- Buffer readahead/cancel-table helpers.
- Recovery inode-get helpers.
- Intent release and finishing helpers.
- `xlog_recover_resv`, which transforms normal transaction reservations into single-logcount reservations for intent replay.

Important behavior:
- Intent recovery pass2 reconstructs in-core intent items or releases them when done items are found.
- Reduced logcount for recovered intents avoids grant-space livelocks when recovered intents pin the log tail.

Integration:
- Used by log recovery implementation and deferred operation replay.
- Depends directly on log item type constants and formats from `xfs_log_format.h`.

Risk notes:
- Item ordering is central to safe replay, especially cancelled buffers and inode buffers.
- Reservation transformation is subtle and prevents recovery-time log-space deadlock.
