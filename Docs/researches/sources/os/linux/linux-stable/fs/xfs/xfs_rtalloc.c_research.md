# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_rtalloc.c

## Purpose
Implements XFS realtime volume allocation, realtime growfs, realtime mount/unmount initialization, realtime free-extent counter rebuild, and bmap integration for realtime data allocation.

## Main APIs
- `xfs_bmap_rtalloc` is the bmap allocator entry point for realtime inodes.
- `xfs_rtallocate_rtgs` allocates realtime extents across rtgroups using a rotating starting group or block hint.
- `xfs_growfs_rt` grows the realtime device and updates bitmap, summary, rtgroup, rtsb, and superblock metadata.
- `xfs_growfs_check_rtgeom` validates proposed realtime geometry and log-space feasibility.
- `xfs_rtmount_readsb`, `xfs_rtmount_freesb`, `xfs_rtmount_init`, `xfs_rtmount_inodes`, and `xfs_rtunmount_inodes` manage realtime mount metadata.
- `xfs_rtalloc_reinit_frextents` recomputes free realtime extent counters from bitmap contents.

## Key Behavior
Realtime allocation uses bitmap and summary metadata to find extents by exact start, near a hint, or by size. Summary lookups can be accelerated by an rtgroup summary cache recording the highest useful level per bitmap block. Allocation updates summary counts for the old free extent and any pre/post free fragments, then marks the allocated bitmap range.

Allocation length and placement honor realtime extent size, extent size hints, CoW extent hints for CoW fork allocation, product alignment, request min/max bounds, and end-of-volume clamping. If alignment-driven allocation fails, `xfs_bmap_rtalloc` retries with the original request and no hint alignment. Pre-rtgroup filesystems can use the bitmap inode atime as a spreading sequence for first allocations in new realtime files.

Rtgroup allocation iterates groups from a hinted group or rotor, locks bitmap metadata, searches near or by size, adjusts for busy extents on rtgroup-enabled filesystems by trimming or flushing/waiting, joins the rtgroup to the transaction, updates the bitmap/summary, decrements free realtime counters, and returns a filesystem block and length.

Growfs uses a fake mount with proposed geometry to compute derived fields and transaction reservations. It initializes or extends rt bitmap and summary files, copies summary data when summary geometry changes, writes the realtime superblock when adding an rtsb-backed realtime volume, initializes rtrmap state for the rtsb, frees newly added realtime extents into the bitmap, updates superblock fields and free counters, recalculates rsum values and btree maxlevels, and updates secondary superblocks plus metafile reservations.

Rtgroup grow supports extending the last partial group and allocating new rtgroups. Zoned realtime grow follows a separate path that updates superblock geometry and makes new zones available instead of bitmap/summary freeing. Geometry checks reject unsupported shrink, invalid extent sizes, unsupported quota/rmap/reflink combinations on non-rtgroup filesystems, non-rtgroup reflink realtime extent sizes, excessive summary-vs-log sizing, and zoned sizes not aligned to rtgroup size.

Mount-time code reads and pins the realtime superblock when present, verifies realtime device availability and size, computes summary blocks/levels, loads rtgroup metadata inodes, preloads their extent maps to allow shared-lock bitmap scans, and allocates summary caches except on zoned filesystems. Unmount releases per-rtgroup metadata inodes and summary caches.

## Dependencies
Uses realtime bitmap/summary helpers, rtgroup metadata and locks, rt metadata inodes, realtime superblock verifiers, transaction reservations, bmap extent-size alignment, quota reservation accounting, busy extent tracking, rtrmap and rtrefcount btree maxlevel computation, metafile reservations, zoned allocation, health/error reporting, and secondary superblock updates.

## Failure Handling
Read-only capability checks, missing rtdev, last-block read failures, invalid geometry, summary corruption, allocation exhaustion, busy extents, transaction failures, and metadata initialization failures propagate errno. Growfs attempts to keep completed rtgroup growth reflected in secondary superblocks even after partial errors and restores rtgroup geometry/summary-cache state on per-group grow failure.
