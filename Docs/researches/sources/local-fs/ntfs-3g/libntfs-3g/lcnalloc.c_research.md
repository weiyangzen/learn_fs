# File Research: sources/local-fs/ntfs-3g/libntfs-3g/lcnalloc.c

## Purpose
Provides cluster allocation and deallocation over the volume LCN bitmap, respecting NTFS MFT-zone reservation and reducing fragmentation through zone cursors and run coalescing.

## Main Interfaces
- `ntfs_cluster_alloc()` allocates clusters and returns a runlist.
- `ntfs_cluster_free_from_rl()` frees all non-sparse runs in a runlist.
- `ntfs_cluster_free_basic()` frees a single LCN/count range.
- `ntfs_cluster_free()` frees clusters from an attribute runlist starting at a VCN.
- Internal helpers maintain zone cursors, full-zone state, bitmap writeback, and empty-run discovery.

## Control Flow
The allocator scans `$BITMAP` in 4096-byte buffers. It starts either from a caller hint or from the relevant zone cursor. It searches zones in passes: current point to zone end, then zone start to current point, then switches among MFT, data1, and data2 zones. Free bits are set in memory, contiguous LCNs are coalesced into runlist entries, bitmap chunks are written back, volume free-cluster counters are updated, and zone cursors advance with a skip distance.

On error, the partial runlist is terminated, dumped for debugging, freed through `ntfs_cluster_free_from_rl()`, and discarded.

## Integration Points
Uses `$BITMAP` through `vol->lcnbmp_na`, bitmap helpers, runlist helpers, `ntfs_attr_pread/pwrite`, and volume fields such as `mft_zone_start`, `mft_zone_end`, `data*_zone_pos`, `mft_zone_pos`, `full_zones`, and free-cluster counters.

## Risks and Invariants
- Partial allocation rollback relies on the runlist being validly terminated.
- Free counters are adjusted optimistically and checked against `nr_clusters`.
- `ntfs_cluster_free()` contains FIXME notes for rollback gaps if freeing later runs fails.
- The allocator marks full zones and later clears those marks when a cluster in that zone is freed.
