# File Research: sources/os/linux/linux/fs/xfs/xfs_extfree_item.c

Implements extent-free intent/done log items and deferred extent free operations. These are XFS’s crash-recoverable mechanism for ensuring extents that were scheduled for freeing are either completed or replayed after log recovery.

Key logic:
- EFI lifecycle:
  - `xfs_efi_init` allocates and initializes an EFI with two references.
  - `xfs_efi_item_format`, `xfs_efi_item_unpin`, `xfs_efi_item_release`, and `xfs_efi_item_match` implement log item behavior.
  - `xfs_efi_copy_format` converts recovered 32-bit, 64-bit, or native log formats.
- EFD lifecycle:
  - `xfs_extent_free_create_done` allocates the done item tied to an EFI.
  - `xfs_efd_item_format`, `xfs_efd_item_release`, and `xfs_efd_item_intent` implement done-item behavior.
  - `xfs_efd_from_efi` copies all EFI extents into an EFD when transaction rolling must cancel/relog remaining work.
- Deferred operation support:
  - `xfs_extent_free_defer_add` selects AG vs realtime-group ownership and queues the right defer type.
  - `xfs_extent_free_finish_item` calls `__xfs_free_extent`, fills EFD records, and handles `EAGAIN` by preserving all EFI extents.
  - `xfs_agfl_free_finish_item` frees AGFL blocks specially without busy-list insertion.
  - `xfs_rtextent_free_finish_item` handles realtime frees, including zoned filesystems via `xfs_zone_free_blocks`.
- Recovery:
  - `xfs_extent_free_recover_work` validates all recovered extents, reconstructs deferred work items, allocates a recovery transaction, and commits/captures continued deferred work.
  - `xfs_extent_free_relog_intent` relogs intents to move the log tail.
  - `xlog_recover_efi_commit_pass2`, `xlog_recover_rtefi_commit_pass2`, `xlog_recover_efd_commit_pass2`, and `xlog_recover_rtefd_commit_pass2` rebuild or cancel intents during log replay.
- Exports defer-op tables for normal frees, AGFL frees, and realtime frees, plus recover item ops for EFI/EFD and realtime EFI/EFD.

Important invariants: EFI extent slots must be fully populated before logging; EFDs release EFI references; recovered EFI extents must all validate and must not mix realtime and non-realtime semantics.
