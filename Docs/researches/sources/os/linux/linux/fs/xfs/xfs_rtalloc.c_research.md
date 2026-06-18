# File Research: sources/os/linux/linux/fs/xfs/xfs_rtalloc.c

## Role

Realtime device allocation, mount, unmount, free-space recount, and growfs implementation for XFS. It handles legacy single realtime sections, rtgroups, zoned realtime behavior, realtime metadata inodes, bitmap/summary maintenance, and realtime bmap allocation.

## Main Responsibilities

- Allocation search:
  `xfs_rtany_summary`, `xfs_rtallocate_extent_block`, `xfs_rtallocate_extent_exact`, `xfs_rtallocate_extent_near`, `xfs_rtalloc_sumlevel`, and `xfs_rtallocate_extent_size` search realtime bitmap/summary metadata for free extents that satisfy min/max/alignment constraints.
- Allocation update:
  `xfs_rtallocate_range` marks extents allocated, updates summaries for split free extents, updates bitmap state, and decrements free realtime counters.
- Busy extent handling:
  `xfs_rtalloc_check_busy` and `xfs_rtallocate_adjust_for_busy` trim or wait on busy realtime extents for rtgroup filesystems.
- Realtime bmap allocation:
  `xfs_bmap_rtalloc` aligns allocation requests to realtime extent size and extent-size hints, picks locality hints, calls rtgroup allocation, retries without hint alignment on ENOSPC, and accounts allocation.
- Mount/unmount:
  `xfs_rtmount_readsb`, `xfs_rtmount_freesb`, `xfs_rtmount_init`, `xfs_rtmount_inodes`, `xfs_rtmount_rtg`, and `xfs_rtunmount_inodes` attach realtime superblocks, load realtime metadata inodes, preload their extent maps, and manage summary caches.
- Growfs:
  `xfs_growfs_rt` validates permissions, rt device presence, geometry, feature constraints, log sizing, rtgroup setup, and grows existing/new realtime groups.
- Grow internals:
  fake mount geometry calculation, bitmap/summary file block initialization, summary copying, realtime superblock initialization, superblock field updates, new extent freeing, secondary superblock updates, and metadata reservation reset.
- Free extent recount:
  `xfs_rtalloc_reinit_frextents` scans all rtgroups and resets `sb_frextents`.

## Important Rules

- Realtime shrink is unsupported.
- Realtime extent size can only change when adding the realtime volume.
- Without rtgroups, realtime cannot be combined with rmapbt, quotas, or reflink.
- With reflink, realtime extent size must satisfy `xfs_reflink_supports_rextsize`.
- Zoned realtime grow requires extent size 1 and new size aligned to RT group size.
- Summary size must not exceed log constraints because grow can log large summary updates.
- For initial user data on pre-rtgroup filesystems, `xfs_rtpick_extent` spaces allocations using a sequence stored in the bitmap inode atime.

## Locking and Transactions

Realtime allocation locks bitmap metadata, delays joining rtgroup inodes until committed to an allocation for rtgroup filesystems, and joins bitmap/summary inodes earlier for legacy behavior. Growfs is serialized by `m_growlock`; rtgroup locks protect bitmap/rmap updates.

## Dependencies

Uses realtime bitmap/summary APIs, realtime group/inode APIs, bmap allocation, transactions, quotas, health/error handling, rmap/refcount realtime btrees, reflink support checks, zoned allocation, secondary superblock update, and metadata reservations.
