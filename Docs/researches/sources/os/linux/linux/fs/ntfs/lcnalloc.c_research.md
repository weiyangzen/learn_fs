# File Research: sources/os/linux/linux/fs/ntfs/lcnalloc.c

This file implements cluster allocation and deallocation against the NTFS volume LCN bitmap.

Freeing by runlist:
- `ntfs_cluster_free_from_rl_nolock()` clears bitmap runs for all non-negative LCNs in a supplied runlist while the caller holds the volume LCN bitmap write lock.
- It waits until free-cluster accounting is known, skips sparse/sentinel runs, clears `$Bitmap`, accumulates freed clusters, and increments volume free-cluster accounting.

Allocation:
- `ntfs_cluster_alloc()` allocates clusters from either the MFT zone or data zones and returns a new runlist.
- Inputs include starting VCN, count, preferred LCN, zone, extension-vs-hole behavior, contiguous requirement, and deallocation-purpose flag.
- The allocator:
  - Enters NOFS allocation context and takes `vol->lcnbmp_lock`.
  - Checks available free clusters, optionally subtracting dirty clusters.
  - Searches the bitmap in chunks mapped through the page cache.
  - Uses `vol->lcn_empty_bits_per_page` to skip full bitmap pages.
  - Supports an initial hint, current zone positions, two-pass zone search, and fallback across MFT/data zones.
  - Coalesces adjacent allocated clusters into runlist elements.
  - Marks bitmap folios dirty, updates free-cluster accounting, and updates zone cursors.
  - Shrinks the MFT zone when data allocation exhausts ordinary data zones.
  - Terminates returned runlists with `LCN_ENOENT` for extension allocation or `LCN_RL_NOT_MAPPED` for hole filling.
- `max_empty_bit_range()` helps locate the start of the longest zero-bit range within a bitmap buffer.

Rollback and error handling:
- Allocation failure after partial bitmap mutation triggers rollback via `ntfs_cluster_free_from_rl_nolock()`.
- Rollback failure marks the volume erroneous and instructs chkdsk through error logging.
- `-ENOSPC`, `-ENOMEM`, `-EIO`, and `-EINVAL` are returned as error pointers.

Deallocation:
- `__ntfs_cluster_free()` frees clusters described by an inode runlist from a starting VCN and optional count.
- It can use an existing attribute search context or map runlist fragments as needed.
- It clears real cluster bits in `$Bitmap`, skips sparse runs, tracks total logical freed clusters separately from real physical freed clusters, and updates free-cluster accounting.
- If discard is enabled, it issues aligned block discard for freed physical ranges after releasing the bitmap lock.
- On mid-free failure, it recursively calls itself in rollback mode to re-set bitmap bits for already freed clusters.

Locking:
- Allocation and freeing serialize bitmap mutation with `vol->lcnbmp_lock`.
- Freeing requires the inode runlist write lock on entry.
- NOFS allocation context avoids filesystem recursion during memory allocation.
- The allocator interacts with folio locking/mapping for `$Bitmap` pages.

Role in subsystem:
This is the physical space manager for NTFS writes, truncation, delayed allocation conversion, and metadata growth. It is directly consumed by attribute mapping/expansion code and indirectly by the iomap write path.
