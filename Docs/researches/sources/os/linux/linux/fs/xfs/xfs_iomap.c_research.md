# File Research: sources/os/linux/linux/fs/xfs/xfs_iomap.c

## Role
Implements XFS mappings for the kernel iomap layer. It translates XFS bmbt extents into iomaps, allocates or reserves blocks for direct, buffered, DAX, reflink/COW, atomic, zoned, read, seek, xattr, zero, and truncate operations, and supplies the `iomap_ops` tables used throughout XFS I/O.

## Main Structures and Entry Points
- `xfs_bmbt_to_iomap` converts an XFS extent record into a generic `struct iomap`.
- `xfs_iomap_inode_sequence` and `xfs_iomap_valid` provide stale-map detection through data/attr/COW fork sequence cookies.
- `xfs_iomap_write_direct` performs transaction-backed direct-write block allocation or DAX conversion.
- `xfs_direct_write_iomap_begin`, `xfs_buffered_write_iomap_begin`, `xfs_zoned_buffered_write_iomap_begin`, `xfs_zoned_direct_write_iomap_begin`, and `xfs_atomic_write_cow_iomap_begin` are write mapping paths for different I/O modes.
- `xfs_iomap_prealloc_size` and `xfs_bmapi_reserve_delalloc` implement dynamic buffered delayed-allocation reservation and speculative preallocation.
- `xfs_iomap_write_unwritten` converts unwritten extents after I/O completion.
- `xfs_read_iomap_begin`, `xfs_seek_iomap_begin`, and `xfs_xattr_iomap_begin` map reads, seek-data/hole probing, and attr fork access.
- `xfs_zero_range` and `xfs_truncate_page` bridge truncate/zero helpers to DAX or buffered iomap operations.
- Exports several `const struct iomap_ops` and `const struct iomap_write_ops`.

## Behavior
Mapping conversion rejects invalid start blocks, reports holes, delalloc, unwritten, mapped extents, DAX offsets, integrity checksum flags, dirty inode-log state for datasync, and realtime-group merge boundaries. EOF allocation can be aligned to stripe/extent-size hints, and preallocation grows with file size but is throttled by global free space and user/group/project quota watermarks.

Direct writes first read the current mapping, decide if allocation or COW is needed, enforce nowait/overwrite-only constraints, support hardware atomic writes only when one naturally aligned extent spans the write, allocate blocks through transactions when needed, and return source maps for COW. DAX maps convert unwritten extents before data copy and complete COW at iomap end.

Buffered writes use delayed allocation unless extent-size hints or zoned allocation require other paths. They consider data fork and COW fork mappings together, handle unshare and zeroing specially, reserve delalloc blocks and quota, tag EOF/COW speculative preallocations, release unused new delalloc on short writes, and fill dirty folio batches to correctly zero ranges backed transiently by COW/pagecache state.

Atomic software writes allocate and convert COW fork mappings so data can be written out of place. Zoned buffered writes reserve from a caller-provided zone allocation context and map COW fork delalloc, while zoned direct writes report anonymous mappings whose actual extent recording is deferred to I/O completion.

## Interactions
This file is central to XFS I/O and interacts with bmap, reflink, quota, transaction reservation, realtime groups, zoned allocation, inode fork sequence counters, DAX, iomap writeback, pagecache invalidation, and inode operations (`xfs_iops.c` uses zero/truncate helpers and fiemap operations).

## Invariants and Error Handling
- Shutdown filesystems return `-EIO`; nowait paths return `-EAGAIN` rather than blocking on extent reads or allocations.
- Invalid block zero access marks the data fork sick and returns `-EFSCORRUPTED`.
- Atomic hardware writes require natural alignment, one covering extent, and size within the block device atomic write limit.
- Delalloc reservations update quota, free block/free realtime counters, `i_delayed_blks`, and delalloc accounting together, with rollback on failure.
- New delalloc mappings are flagged `IOMAP_F_NEW` so failed buffered writes can punch unused reservations.
- COW maps use `IOMAP_F_SHARED` and include validity cookies spanning data and COW fork sequences.
