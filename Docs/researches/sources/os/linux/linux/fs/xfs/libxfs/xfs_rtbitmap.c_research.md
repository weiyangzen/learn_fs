# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_rtbitmap.c

Implements realtime bitmap and summary file operations shared with userspace-facing XFS logic. It manages rt bitmap/summary buffer verification, cached buffer access, bit scanning/modification, summary counter updates, realtime extent freeing, free-space queries, geometry calculations, and bitmap/summary file initialization.

Key responsibilities:
- Verifies rtgroup bitmap/summary buffer headers, CRCs, UUIDs, LSNs, owner inode, and block number.
- Provides buffer ops for legacy rt buffers and rtgroup bitmap/summary buffers.
- Caches one bitmap and one summary buffer in `xfs_rtalloc_args`.
- Reads bitmap/summary blocks through the rtgroup inode bmap and transaction buffer APIs.
- Finds free/allocated extent boundaries backward and forward using word-level bitmap scans.
- Modifies summary counters and maintains the per-rtgroup summary cache.
- Sets/clears ranges of bitmap bits and logs the modified byte spans.
- Frees realtime extents by updating bitmap, adjacent free-extent summaries, and superblock free extent count.
- Validates allocation state in debug builds before freeing.
- Frees block-count based realtime ranges after alignment checks.
- Iterates free realtime extents over a range or entire rtgroup.
- Tests whether an rt extent range is free.
- Computes bitmap and summary file block counts, including rtgroup header overhead and zoned mode behavior.
- Allocates and initializes bitmap/summary file blocks for growfs.
- Initializes rtbitmap/rtsummary inode sizes.

Important functions:
- `xfs_rtbitmap_read_buf`, `xfs_rtsummary_read_buf`, `xfs_rtbuf_cache_relse`
- `xfs_rtfind_back`, `xfs_rtfind_forw`
- `xfs_rtmodify_summary`, `xfs_rtget_summary`
- `xfs_rtmodify_range`, `xfs_rtfree_range`
- `xfs_rtcheck_range`
- `xfs_rtfree_extent`, `xfs_rtfree_blocks`
- `xfs_rtalloc_query_range`, `xfs_rtalloc_query_all`
- `xfs_rtalloc_extent_is_free`
- `xfs_rtbitmap_rtx_per_rbmblock`, `xfs_rtbitmap_blockcount`, `xfs_rtsummary_blockcount`
- `xfs_rtfile_initialize_blocks`, `xfs_rtbitmap_create`, `xfs_rtsummary_create`

Design notes:
- In rtgroups, bitmap/summary blocks contain `xfs_rtbuf_blkinfo` headers and store words big-endian; legacy files use older native word layout.
- Zoned filesystems return zero bitmap/summary block counts and reject rt bitmap queries.
- Freeing all realtime blocks on pre-rtgroup filesystems resets the bitmap inode sequence marker behavior.
