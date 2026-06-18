# File Research: sources/os/linux/linux/fs/ntfs/iomap.c

This file implements the NTFS bridge to Linux iomap for buffered reads/writes, direct I/O mapping, page fault write mapping, zeroing, seek reporting, and writeback.

Read path:
- Resident attributes are mapped as `IOMAP_INLINE`: the resident value is copied from the MFT attribute record into a temporary zeroed page and released in `ntfs_read_iomap_end`.
- Non-resident attributes map file offsets through the NTFS runlist using `ntfs_attr_vcn_to_rl`.
- Holes, delayed allocation, mapped extents, and optionally unwritten extents are translated into `IOMAP_HOLE`, `IOMAP_DELALLOC`, `IOMAP_MAPPED`, or `IOMAP_UNWRITTEN`.
- The code treats NTFS initialized-size semantics carefully: NTFS has a single initialized boundary rather than arbitrary unwritten extent ranges. Seek operations request mapped behavior beyond initialized size so preallocated space is not misreported as a hole.

Zeroing and folio completion:
- `ntfs_iomap_put_folio_non_resident()` zeroes folio regions around `initialized_size` to prevent exposing stale disk/cache data when iomap zeroing touches beyond initialized data.
- `ntfs_iomap_valid()` checks whether a cached iomap still corresponds to a delayed allocation runlist entry; stale zero-range mappings cause `ntfs_zero_read_iomap_end()` to return `-EPERM`.
- `ntfs_dio_zero_range()` issues block-device zeroout for sector-aligned direct I/O ranges.

Write path:
- `__ntfs_write_iomap_begin()` rejects writes on shutdown volumes, expands attributes when writes exceed `data_size`, then dispatches resident or non-resident handling.
- Resident writes use inline iomap data copied from the resident attribute into a temporary page; `ntfs_write_iomap_end_resident()` copies modified bytes back into the MFT attribute and marks the MFT record dirty.
- Simple buffered non-resident writes can mark holes as `LCN_DELALLOC`, merge delayed-allocation runs into the runlist, hold dirty cluster accounting, and zero partial boundary clusters when needed.
- Delayed allocation/direct/page-mkwrite/writeback mapping is handled by `ntfs_write_da_iomap_begin_non_resident()`, which calls `ntfs_attr_map_cluster()` to allocate/map clusters and optionally update mapping pairs immediately for direct I/O, mkwrite, system files, or attribute inodes.
- Writes past `initialized_size` call `ntfs_extend_initialized_size()` before mapping, and page-mkwrite can update initialized size after mapping.

Exported operation tables:
- `ntfs_read_iomap_ops`
- `ntfs_write_iomap_ops`
- `ntfs_seek_iomap_ops`
- `ntfs_page_mkwrite_iomap_ops`
- `ntfs_dio_iomap_ops`
- `ntfs_writeback_ops`
- `ntfs_iomap_folio_ops`

Locking and error behavior:
- Runlist locks are taken for read/write around mapping and mutation.
- `mrec_lock` protects MFT attribute expansion and mapping-pair updates.
- Corrupt zero-length physical runs produce `-EIO`; invalid runlist states usually produce `-EINVAL` or `-EIO`; allocation/metadata failures propagate negative errno.
- The file is tightly coupled to `attrib.h`, `mft.h`, `inode.h`, `volume.h`, and Linux iomap/writeback APIs.
