# File Research: sources/os/linux/linux/fs/xfs/xfs_extfree_item.h

Defines kernel-only EFI/EFD log item structures and public helpers.

Key contents:
- `XFS_EFI_MAX_FAST_EXTENTS` and `XFS_EFD_MAX_FAST_EXTENTS` define cache-backed fast allocation thresholds.
- Extensive comments document EFI reference ownership: one reference for EFI AIL insertion and one held by the EFD path, preventing premature free across commit/unpin ordering.
- `struct xfs_efi_log_item` embeds `xfs_log_item`, refcount, next-extent counter, and variable EFI log format.
- `xfs_efi_log_item_sizeof` computes variable-sized EFI allocation.
- `struct xfs_efd_log_item` embeds `xfs_log_item`, points to its EFI, tracks next extent, and stores variable EFD format.
- Declares EFI/EFD slab caches, `xfs_extent_free_defer_add`, and log-space calculators.

This header is the structural contract for crash-recoverable deferred extent freeing.
