# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_exchmaps_item.h

## Purpose
Declares in-core log item structures and public deferred-add helper for file mapping exchange intents.

## Main Types
`struct xfs_xmi_log_item` embeds the common log item, an atomic reference count, and the logged XMI format. `struct xfs_xmd_log_item` embeds a done log item, points to the associated XMI, and stores the XMD format.

## Design Contract
The header documents redo-style logging: the intent item is logged in the first transaction of a rolled sequence, and done items are logged with the bmap updates that complete the exchange. If a crash occurs between intent and final done item, recovery replays the remaining mapping exchanges.

## API
Declares external XMI/XMD slab caches and `xfs_exchmaps_defer_add`.
