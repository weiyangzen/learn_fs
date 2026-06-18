# File Research: sources/os/linux/linux/fs/xfs/xfs_discard.c

Implements XFS FITRIM/discard support for data and realtime devices.

Key behavior:
- Data-device trimming walks AG free-space btrees in bounded batches, marks selected free extents busy-under-discard while holding AGF protection, then issues discards asynchronously.
- `xfs_discard_extents` chains discard bios and clears busy extents from workqueue completion.
- The trim cursor can scan by block number for subrange trims or by extent length for whole-AG trims.
- Busy extents are skipped to avoid discarding blocks that might still be unsafe to reuse.
- Realtime support has two paths: classic realtime device extents use synchronous discard under rtbitmap locking, while rtgroups use the same busy-extent asynchronous machinery as AGs.
- `xfs_ioc_trim` validates privileges, discard capability, no-recovery state, userspace range, granularity, minlen, data/realtime address mapping, and copies the effective range back to userspace.

This file’s design avoids holding AGF locks across slow device discard operations, preventing log and transaction stalls during large fstrim runs.
