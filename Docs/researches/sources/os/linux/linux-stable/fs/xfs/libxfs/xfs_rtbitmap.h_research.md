# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_rtbitmap.h

## Scope

Header for realtime bitmap/summary allocation arguments, realtime block/extent conversion helpers, bitmap and summary word accessors, buffer ops selection, free-space query record types, and public realtime bitmap APIs.

## APIs And Types

- Defines `struct xfs_rtalloc_args`, carrying rtgroup, mount, transaction, cached bitmap/summary buffers, and their file offsets.
- Conversion helpers cover rt extent to rt block, rtgroup block to extent, block lengths to rt extent lengths, alignment/modulo checks, file offset rounding to rt extent size, bitmap block/word mapping, and bitmap block to rt extent conversion.
- Bitmap word helpers: `xfs_rbmblock_wordptr`, `xfs_rtbitmap_getword`, `xfs_rtbitmap_setword`.
- Summary helpers: `xfs_rtsumoffs`, `xfs_rtsumoffs_to_block`, `xfs_rtsumoffs_to_infoword`, `xfs_rsumblock_infoptr`, `xfs_suminfo_get`, `xfs_suminfo_add`.
- Buffer ops selection: `xfs_rtblock_ops`.
- Query model: `struct xfs_rtalloc_rec` and `xfs_rtalloc_query_range_fn`.
- Under `CONFIG_XFS_RT`, declares buffer, scan, mutate, free, query, geometry, initialization, and create APIs.
- Without `CONFIG_XFS_RT`, provides `-ENOSYS` stubs for selected APIs.

## Data Model

- Legacy realtime bitmap and summary blocks store native-endian raw words.
- Rtgroup-enabled filesystems store big-endian words after an rt buffer header.
- `m_rtxblklog >= 0` enables shift/mask fast paths for power-of-two realtime extent sizes; otherwise helpers use division/modulo by `sb_reextsize`.

## Dependencies

- Includes `xfs_rtgroup.h` and depends on mount group geometry, realtime superblock fields, raw bitmap/summary word unions, buffer ops declarations, transactions, realtime group inodes, and XFS integer typedefs.

## Invariants And Risks

- Conversion helpers often mask rt block numbers to the rtgroup block mask before deriving extent numbers or offsets.
- Rtgroup and legacy formats differ in endianness and header placement; callers must use the provided accessors instead of direct buffer casts.
- `xfs_rtblock_ops` must match the inode type and filesystem format so verification and checksumming are correct.
