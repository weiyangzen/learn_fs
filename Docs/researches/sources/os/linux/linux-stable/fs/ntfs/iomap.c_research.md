# File Research: sources/os/linux/linux-stable/fs/ntfs/iomap.c

## Summary
Implements NTFS iomap operations for buffered reads/writes, direct I/O, page faults, seeking, zeroing, and writeback. It maps resident attributes as inline data and non-resident attributes through NTFS runlists, including delayed allocation and initialized-size handling.

## Main Responsibilities
- Provide exported `iomap_ops` tables for read, write, seek, page-mkwrite, and direct-I/O paths.
- Provide `ntfs_writeback_ops` and NTFS folio write operations.
- Convert NTFS resident attributes to `IOMAP_INLINE` buffers.
- Convert non-resident runlist entries into mapped, hole, delalloc, or unwritten iomaps.
- Expand attributes and initialized size before writes when needed.
- Allocate or convert delayed extents during write, fault, DIO, and writeback mapping.
- Zero partial clusters or folio regions that could expose uninitialized bytes.

## Key APIs
- `ntfs_read_iomap_ops`, `ntfs_write_iomap_ops`, `ntfs_seek_iomap_ops`.
- `ntfs_page_mkwrite_iomap_ops`, `ntfs_dio_iomap_ops`.
- `ntfs_writeback_ops`.
- `ntfs_iomap_folio_ops`.
- `ntfs_dio_zero_range()`.

## Important Behavior
Resident reads and writes allocate a temporary page, copy the resident attribute value from the MFT record, expose it as `IOMAP_INLINE`, then copy written inline data back to the resident attribute and dirty the MFT record.

Non-resident reads map VCNs through the runlist. For normal reads, bytes beyond `initialized_size` can be reported as `IOMAP_UNWRITTEN`; seek and zero paths deliberately treat preallocated NTFS space as mapped because NTFS models unwritten state as a single `initialized_size` boundary rather than per-extent unwritten records.

Buffered writes can first mark holes as `LCN_DELALLOC`, hold dirty-cluster accounting, and later call `ntfs_attr_map_cluster()` to allocate real clusters. Direct I/O and page-mkwrite paths allocate/update mapping immediately and zero edge clusters with block zeroout when newly allocated space is partially covered.

## State and Synchronization
The code coordinates `mrec_lock`, `runlist.lock`, NTFS volume shutdown state, dirty-cluster accounting, `i_dealloc_clusters`, `allocated_size`, `data_size`, and `initialized_size`. Cached iomaps for zeroing are validated against the runlist so stale delayed-allocation mappings do not zero data that has since been written.

## Risks
Correctness depends on not exposing data beyond `initialized_size`, especially around partial-cluster writes, stale iomaps, and transitions from holes to delayed or real allocations. Several paths unlock `mrec_lock` inside lower helpers, so callers must preserve the expected lock protocol. Resident inline mappings use temporary pages stored in `iomap->private`, making begin/end pairing mandatory.
