# File Research: sources/os/linux/linux-stable/fs/ntfs/lcnalloc.c

## Summary
Implements NTFS cluster allocation and deallocation against the volume LCN bitmap. It manages MFT/data allocation zones, free-cluster accounting, dirty-cluster reservations, runlist construction, rollback, and optional discard on free.

## Main Responsibilities
- Free all real clusters described by a runlist with the LCN bitmap lock already held.
- Allocate clusters from the MFT zone or data zones while respecting hints, contiguity requests, and current zone cursors.
- Scan bitmap folios for free bits and coalesce allocated bits into runlist elements.
- Shrink the reserved MFT zone when data allocation exhausts normal data zones.
- Free clusters from an inode runlist, mapping unmapped fragments when needed.
- Roll back partial allocation/free failures and mark the volume erroneous if rollback fails.

## Key APIs
- `ntfs_cluster_free_from_rl_nolock()`.
- `ntfs_cluster_alloc()`.
- `__ntfs_cluster_free()`.
- `max_empty_bit_range()` as a local bitmap scan accelerator.

## Important Behavior
`ntfs_cluster_alloc()` waits until free-cluster accounting is known, takes `vol->lcnbmp_lock`, accounts for dirty delayed allocations unless allocating for deallocation, scans the requested zone(s), sets free bitmap bits to allocated, decrements free-cluster counters, updates `lcn_empty_bits_per_page`, and returns a terminated runlist. Termination differs by allocation purpose: extension runlists end with `LCN_ENOENT`, hole-filling runlists with `LCN_RL_NOT_MAPPED`.

The allocator treats the MFT zone separately from data zone 1 and data zone 2. It starts from caller hints or persisted zone positions, does wraparound passes within zones, switches zones as needed, and can halve the MFT zone to make space for data allocations.

`__ntfs_cluster_free()` clears bitmap runs, increments free-cluster accounting, supports sparse runs, maps unmapped runlist fragments, and optionally issues discard aligned to device granularity after successful frees.

## State and Synchronization
Uses `memalloc_nofs_save()`, `vol->lcnbmp_lock`, the `$Bitmap` inode mapping, bitmap folio locking/kmap, `free_clusters`, `dirty_clusters`, zone cursor fields, `lcn_empty_bits_per_page`, and the caller-held inode runlist write lock for inode-based frees.

## Risks
The allocator mutates several pieces of persistent and in-memory allocation state together; partial failures require rollback while still holding the bitmap lock. A failed rollback explicitly leaves inconsistent metadata and sets the volume error flag. Zone switching and bitmap-page accounting are subtle, especially when allocation starts from a hint or when the MFT zone is shrunk.
