# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_iomap.c

This file implements XFS integration with the Linux iomap infrastructure for reads, buffered writes, direct writes, DAX writes, atomic writes, xattrs, seek/data-hole mapping, zeroing, truncation, delayed allocation, CoW, realtime, and zoned allocation.

Core mapping helpers:
- `xfs_iomap_inode_sequence` builds validity cookies from data, attr, and CoW fork sequence counters.
- `xfs_iomap_valid` lets iomap detect stale mappings after extent-tree changes.
- `xfs_bmbt_to_iomap` converts XFS bmbt records to `struct iomap`, handling holes, delalloc, mapped, unwritten, DAX device offsets, integrity flags, dirty datasync state, realtime group boundaries, and validity cookies.
- `xfs_hole_to_iomap` builds hole mappings.
- `xfs_iomap_end_fsb` bounds byte ranges by maximum file size.

Allocation sizing:
- `xfs_eof_alignment` and `xfs_iomap_eof_align_last_fsb` align EOF allocations to stripe, swalloc, and extent-size hint boundaries.
- `xfs_iomap_prealloc_size` computes dynamic speculative preallocation from file extent history, filesystem low-space thresholds, realtime free space, and quota preallocation watermarks.
- `xfs_aligned_fsb_count` is exported by the header as a helper to round allocation lengths to extent-size hints.

Direct writes:
- `xfs_direct_write_iomap_begin` maps or allocates blocks for direct writes and zeroing.
- It handles NOWAIT, overwrite-only, DAX conversion, shared/reflink CoW allocation, hardware atomic write constraints, EOF dirty signaling, and bounded allocation chunks.
- `xfs_iomap_write_direct` performs transactional block allocation or DAX unwritten conversion and returns an updated sequence cookie.

Unwritten extent conversion:
- `xfs_iomap_write_unwritten` loops over a written byte range, converting unwritten extents to written extents transactionally and optionally updating inode size and disk size.

Atomic writes:
- Hardware atomic writes are checked with `xfs_bmap_hw_atomic_write_possible`.
- `xfs_atomic_write_cow_iomap_begin` implements software atomic writes through the CoW fork by allocating/converting CoW mappings and returning shared iomaps.

Buffered writes and delayed allocation:
- `xfs_bmap_add_extent_hole_delay` merges or inserts delalloc extent records into the in-core extent tree and adjusts indirect block reservations.
- `xfs_bmapi_reserve_delalloc` reserves quota, free blocks or realtime extents, indirect blocks, updates delayed block accounting, inserts delalloc extents, and tags EOF or CoW preallocation.
- `xfs_buffered_write_iomap_begin` handles normal buffered writes, reflink CoW writes, unshare, zeroing, dirty-folio lookup, speculative EOF preallocation, data-fork and CoW-fork delalloc, and conversion of post-EOF delalloc during zeroing.
- `xfs_buffered_write_iomap_end` releases newly allocated delalloc blocks after short or failed writes, using invalidate locking when needed.
- `xfs_zoned_buffered_write_iomap_begin` is the zoned realtime variant, using caller-provided zone allocation context and CoW fork delalloc reservations.

Other iomap operations:
- `xfs_zoned_direct_write_iomap_begin` returns anonymous direct-write mappings for zoned realtime writes after ensuring data extents are loaded.
- `xfs_dax_write_iomap_end` finishes or cancels CoW for DAX writes.
- `xfs_read_iomap_begin` maps reads and optionally trims around shared extents for reporting or DAX.
- `xfs_seek_iomap_begin` supports SEEK_DATA/SEEK_HOLE style mapping, including CoW fork dirty data as unwritten.
- `xfs_xattr_iomap_begin` maps remote attribute fork extents.
- `xfs_zero_range` and `xfs_truncate_page` dispatch zero/truncate operations to DAX or buffered iomap paths.

Registered ops:
- `xfs_iomap_write_ops`
- `xfs_direct_write_iomap_ops`
- `xfs_zoned_direct_write_iomap_ops`
- `xfs_atomic_write_cow_iomap_ops`
- `xfs_dax_write_iomap_ops`
- `xfs_buffered_write_iomap_ops`
- `xfs_read_iomap_ops`
- `xfs_seek_iomap_ops`
- `xfs_xattr_iomap_ops`

Risk notes:
- The file is concurrency-sensitive: it coordinates inode locks, extent sequence validation, NOWAIT behavior, page cache dirty state, direct I/O races, and CoW fork state.
- Delalloc accounting spans quota reservations, free block counters, realtime extents, inode delayed block counts, and global delalloc accounting.
- Zeroing over CoW and dirty page cache has explicit race handling; this is an area to inspect carefully for behavioral changes.
- Atomic write support has strict mapping, alignment, and single-extent requirements.
