# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_rtbitmap.c

## Scope

Implements realtime bitmap and summary file buffer access, verification, bitmap scanning/modification, summary updates, realtime extent freeing, free-space queries, geometry calculations, and initialization helpers for realtime bitmap/summary inode blocks.

## APIs And Entry Points

- Buffer/cache helpers: `xfs_rtbuf_cache_relse`, `xfs_rtbitmap_read_buf`, `xfs_rtsummary_read_buf`.
- Bitmap scanning: `xfs_rtfind_back`, `xfs_rtfind_forw`, `xfs_rtcheck_range`.
- Bitmap/summary mutation: `xfs_rtmodify_range`, `xfs_rtmodify_summary`, `xfs_rtget_summary`, `xfs_rtfree_range`.
- Freeing: `xfs_rtfree_extent`, `xfs_rtfree_blocks`.
- Querying: `xfs_rtalloc_query_range`, `xfs_rtalloc_query_all`, `xfs_rtalloc_extent_is_free`.
- Geometry: `xfs_rtbitmap_rtx_per_rbmblock`, `xfs_rtbitmap_blockcount_len`, `xfs_rtbitmap_blockcount`, `xfs_rtsummary_blockcount`.
- Initialization: `xfs_rtfile_initialize_blocks`, `xfs_rtbitmap_create`, `xfs_rtsummary_create`.
- Buffer ops: `xfs_rtbuf_ops`, `xfs_rtbitmap_buf_ops`, `xfs_rtsummary_buf_ops`.

## Data Model

- The realtime bitmap tracks free/allocated realtime extents; bit value 1 means free and 0 means allocated.
- The realtime summary tracks counts of free extents by `log2(length)` and bitmap block number.
- With realtime groups enabled, bitmap and summary blocks contain `struct xfs_rtbuf_blkinfo` headers with magic, owner inode, block address, LSN, and metadata UUID.
- `struct xfs_rtalloc_args` caches one bitmap buffer and one summary buffer for repeated operations.

## Control Flow

- Buffer acquisition:
  - `xfs_rtbuf_get` maps bitmap/summary file blocks through `xfs_bmapi_read`, reads the underlying device buffer with the correct ops, verifies owner for rtgroup formats, and caches the buffer in `xfs_rtalloc_args`.
- Scanning:
  - `xfs_rtfind_back` scans backward from a start extent until bitmap state changes.
  - `xfs_rtfind_forw` scans forward from start to limit until bitmap state changes.
  - `xfs_rtcheck_range` verifies a full range is all free or all allocated and returns the first mismatch.
- Mutation:
  - `xfs_rtmodify_range` sets/clears bitmap bits across partial words, whole words, and block boundaries, logging modified word ranges.
  - `xfs_rtmodify_summary` updates a summary counter and maintains the rtgroup summary cache when present.
  - `xfs_rtfree_range` marks a range free, finds neighboring free runs, removes stale summary counts for split runs, and adds the merged free extent summary.
- Freeing:
  - `xfs_rtfree_extent` verifies the range is allocated in debug builds, frees it, updates superblock free extents, and preserves legacy pre-rtgroup bitmap sequence behavior.
  - `xfs_rtfree_blocks` validates block alignment to realtime extent size, frees by realtime extents, and marks busy rtgroup blocks for rtgroup filesystems.
- Initialization:
  - `xfs_rtfile_initialize_blocks` allocates file blocks for bitmap/summary inodes and initializes each block in its own transaction.
  - `xfs_rtfile_initialize_block` writes rtgroup metadata headers when needed and fills data from a source buffer or zeroes.

## Dependencies

- Uses transaction buffer APIs, bmap reads/writes, realtime allocation arguments, realtime group inode accessors, inode locking/logging, superblock accounting, metadata buffer verification, checksum/LSN validation, extent-busy tracking, error tags, health marking, and mount geometry fields.

## Invariants And Risks

- All block and length arguments to `xfs_rtfree_blocks` must be aligned to realtime extent size.
- Bitmap and summary caches must be released after operations to drop transaction buffer references.
- Summary updates must reflect merged free extents exactly, or allocator free-space discovery becomes incorrect.
- Rtgroup bitmap/summary buffers require owner, UUID, block address, magic, checksum, and LSN validation.
- Zoned realtime configurations return zero bitmap/summary block counts and reject bitmap queries.
