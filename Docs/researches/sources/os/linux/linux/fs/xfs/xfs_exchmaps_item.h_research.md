# File Research: sources/os/linux/linux/fs/xfs/xfs_exchmaps_item.h

Declares in-core XFS exchange-mapping intent and done log item structures.

Key contents:
- Documents that XMI records the first transaction of a rolled exchange operation and XMD records completion with the bmbt updates.
- `struct xfs_xmi_log_item` embeds a common log item, refcount, and on-disk XMI log format.
- `struct xfs_xmd_log_item` embeds a common log item, points to the associated XMI, and stores the XMD log format.
- Exposes XMI/XMD slab caches and `xfs_exchmaps_defer_add`.

This header is the public logging/defer interface for exchange-range mapping operations.
