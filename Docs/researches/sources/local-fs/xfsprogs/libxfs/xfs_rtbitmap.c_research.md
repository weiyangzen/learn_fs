# File Research: sources/local-fs/xfsprogs/libxfs/xfs_rtbitmap.c

Implements realtime allocator bitmap and summary file operations shared with userspace. It verifies realtime bitmap/summary buffers, caches bitmap/summary reads, scans and modifies bitmap bits, updates summary counters, frees realtime extents, queries free realtime extents, computes realtime metadata geometry, and initializes realtime metadata files during grow/create.

Buffer verification and caching:
- `xfs_rtbuf_verify` validates rtgroup metadata headers: magic, rtgroups feature, CRC feature, metadata UUID, and block address.
- Read verification checks LSN and checksum before structural validation for rtgroup-enabled filesystems.
- Write verification updates LSN and checksum.
- Defines buffer ops for legacy rt buffers and rtgroup bitmap/summary buffers.
- `xfs_rtbuf_cache_relse` releases cached bitmap and summary buffers in `xfs_rtalloc_args`.
- `xfs_rtbuf_get` maps bitmap/summary inode file blocks to disk blocks, reads buffers, verifies rtgroup owner, tags buffer type, and caches the result.

Bitmap scanning:
- `xfs_rtfind_back` scans backward from a realtime extent until allocation/free state changes.
- `xfs_rtfind_forw` scans forward to a limit until allocation/free state changes.
- Both functions operate word-at-a-time with partial-word masks across bitmap blocks.
- `xfs_rtcheck_range` verifies that a range is all free or all allocated, returning the first mismatching extent.
- Debug-only `xfs_rtcheck_alloc_range` asserts that an extent is allocated before freeing.

Bitmap and summary modification:
- `xfs_rtmodify_range` sets a range of bitmap bits to free or allocated and logs modified word ranges.
- `xfs_rtmodify_summary` adjusts summary counters for a `(log2 extent size, bitmap block)` bucket and updates the per-rtgroup summary cache if present.
- `xfs_rtget_summary` reads a summary counter.
- `xfs_rtfree_range` marks realtime extents free, finds adjacent free extents, removes old summary records for neighboring fragments, and adds the merged free extent summary.

Freeing APIs:
- `xfs_rtfree_extent` frees an extent in realtime-extents units, updates the realtime bitmap/summary, increments superblock free extent count, and handles legacy all-free bitmap sequence reset behavior.
- `xfs_rtfree_blocks` accepts realtime block units, enforces realtime extent alignment, converts to rtextents, calls `xfs_rtfree_extent`, and marks rtgroup busy extents when rtgroups are enabled.

Free-space queries:
- `xfs_rtalloc_query_range` walks the bitmap over a requested extent range and invokes a callback for each free run.
- `xfs_rtalloc_query_all` scans all realtime extents in an rtgroup.
- `xfs_rtalloc_extent_is_free` checks whether a given extent is entirely free.

Geometry helpers:
- `xfs_rtbitmap_rtx_per_rbmblock` accounts for rtgroup headers reducing usable bitmap payload.
- `xfs_rtbitmap_blockcount_len` returns bitmap blocks needed for a number of realtime extents, with zoned filesystems returning zero.
- `xfs_rtbitmap_blockcount` and `xfs_rtsummary_blockcount` compute filesystem/rtgroup metadata file sizes and summary levels.

Metadata file initialization:
- `xfs_rtfile_alloc_blocks` allocates file blocks to bitmap or summary inodes.
- `xfs_rtfile_initialize_block` initializes one metadata block, writing rtgroup headers when enabled and copying or zeroing payload.
- `xfs_rtfile_initialize_blocks` allocates and initializes a file range one mapped extent at a time.
- `xfs_rtbitmap_create` and `xfs_rtsummary_create` set inode disk sizes and log inode core state.

Important interactions:
- Uses `xfs_rtbitmap.h` conversion and word access helpers.
- Uses bmap to map rt bitmap/summary inode blocks.
- Marks realtime metadata inodes sick on corrupt mappings or metadata buffers.
- Updates superblock free extent counters through transactions.
- Rejects bitmap query/free logic for zoned mode where appropriate.
