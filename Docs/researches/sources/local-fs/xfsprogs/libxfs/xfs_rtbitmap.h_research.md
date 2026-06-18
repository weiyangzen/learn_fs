# File Research: sources/local-fs/xfsprogs/libxfs/xfs_rtbitmap.h

Header for realtime bitmap/summary helpers, conversion routines, free-space query types, and realtime allocator function declarations.

Core state:
- `struct xfs_rtalloc_args` carries rtgroup, mount, transaction, cached bitmap/summary buffers, and cached file offsets.

Realtime conversion helpers:
- Converts between realtime extent numbers, realtime block numbers, rtgroup block numbers, file block offsets, and lengths.
- Optimizes power-of-two realtime extent sizes through `m_rtxblklog`; otherwise uses division/modulo by `sb_rextsize`.
- Provides alignment helpers such as `xfs_extlen_to_rtxmod`, `xfs_blen_to_rtxoff`, `xfs_rtb_to_rtxoff`, and file offset rounding to realtime extent size.
- Handles rtgroup-relative masking for realtime block conversions.

Bitmap layout helpers:
- `xfs_rtx_to_rbmblock`, `xfs_rtx_to_rbmword`, and `xfs_rbmblock_to_rtx` map realtime extents to bitmap file locations.
- `xfs_rbmblock_wordptr` returns the correct bitmap word pointer, skipping rtgroup metadata headers when present.
- `xfs_rtbitmap_getword` and `xfs_rtbitmap_setword` abstract legacy native-endian words versus rtgroup big-endian words.

Summary layout helpers:
- `xfs_rtsumoffs` maps `(log2 length, bitmap block)` to summary word offset.
- `xfs_rtsumoffs_to_block` and `xfs_rtsumoffs_to_infoword` map summary offsets to file block and word positions.
- `xfs_rsumblock_infoptr`, `xfs_suminfo_get`, and `xfs_suminfo_add` abstract legacy and rtgroup summary word formats.

Buffer ops selection:
- `xfs_rtblock_ops` returns rtgroup-specific bitmap/summary buffer ops when rtgroups are enabled, otherwise legacy realtime buffer ops.

Query model:
- `struct xfs_rtalloc_rec` represents a free realtime extent run.
- `xfs_rtalloc_query_range_fn` is the callback signature for walking free realtime extents.

Declared APIs under `CONFIG_XFS_RT`:
- Buffer cache/read helpers for bitmap and summary files.
- Bitmap scanning/modification helpers: check range, find backward/forward, modify range.
- Summary get/modify helpers.
- Freeing APIs: `xfs_rtfree_range`, `xfs_rtfree_extent`, `xfs_rtfree_blocks`.
- Query APIs: range/all query and extent-is-free.
- Geometry APIs: bitmap extents per block, bitmap block counts, summary block count.
- Metadata initialization/create helpers for bitmap and summary files.

Fallback behavior:
- Without `CONFIG_XFS_RT`, most realtime APIs return `-ENOSYS` or zero-like stubs, allowing non-realtime builds to compile while rejecting runtime realtime operations.
