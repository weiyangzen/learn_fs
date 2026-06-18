# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_exchmaps_item.c

## Purpose
Implements log intent/done items for deferred file mapping exchange operations (`XMI`/`XMD`), including transaction formatting, deferred-op integration, recovery, relogging, and intent cancellation.

## Main Types and Caches
Uses `xfs_xmi_cache` for exchange mapping intent items and `xfs_xmd_cache` for done items. XMI items carry inode numbers/generations, start offsets, block count, sizes, flags, and a unique intent id. XMD items reference an XMI and log completion by id.

## Log Item Lifecycle
XMI allocation sets a two-reference count: one for log/unpin and one for done/cancel processing. Release removes from the AIL when the last reference drops. XMD release drops the associated XMI reference and frees the done item. XMI match compares intent ids for recovery cancellation.

## Deferred Operation Integration
`xfs_exchmaps_defer_type` supports one item per intent. `create_intent` logs the current exchange request, `create_done` logs completion, `finish_item` calls `xfs_exchmaps_finish_one`, and `cancel_item` frees unfinished in-core requests. `-EAGAIN` means work remains and the intent is requeued after other deferred work to avoid pinning too many XMI items.

## Recovery
XMI recovery validates feature support, padding, flags, inode numbers, and file extents; reopens both inodes by handle including generation checks; estimates resources; locks both inodes; ensures reflink/extent-count prerequisites; finishes the recovered intent; and captures/commits deferred work. XMD recovery releases a matching recovered XMI by id.

## Relogging
`xfs_exchmaps_relog_intent` clones the old XMI format into a fresh XMI so long-running recovery can move the log tail forward.

## Failure Handling
Malformed log vector sizes, nonzero padding, invalid flags/inodes/extents, inode handle failures, or corrupted finish operations return corruption errors and release held inodes/transactions.
