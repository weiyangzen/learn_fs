# File Research: sources/local-fs/xfsprogs/libxfs/xfs_rtrmap_btree.c

This file implements the realtime reverse-mapping btree. It tracks owners of extents in the realtime device, is rooted in a per-rtgroup metadata inode, and differs from the regular rmap btree mainly by inode rooting and by not living in free space.

The btree uses overlapping-key geometry. Internal node key length is two `struct xfs_rmap_key` values per pointer, and the btree ops set `XFS_BTGEO_OVERLAPPING | XFS_BTGEO_IROOT_RECORDS`. Record/key initialization includes startblock, owner, and an offset key with the unwritten bit masked out because unwritten state is a record attribute rather than a key component. High-key creation extends physical startblock by blockcount minus one and extends logical offset only for inode-owner non-bmbt records.

Comparison and ordering logic sorts by physical startblock, owner, then offset keymask. The mask parameter may omit owner/offset comparisons but cannot mask off the physical component. `xfs_rtrmapbt_keys_contiguous` supports contiguity checks only for the physical keyspace component and asserts if asked for more specific owner/offset contiguity.

Verifier functions require valid magic, rmap feature support, a valid v5 long btree header, level within `m_rtrmap_maxlevels`, block structure within per-level max records, and CRCs on disk buffers. `xfs_rtrmapbt_buf_ops` exposes these checks.

The root-reallocation path mirrors the rtrefcount implementation. Because an inode-root internal node stores paired low/high keys before pointers, `xfs_rtrmapbt_move_ptrs` and `xfs_rtrmapbt_broot_realloc` move pointers when root buffer size changes. Assertions ensure the corresponding on-disk root will fit the inode fork.

`xfs_rtrmapbt_ops` defines the disk btree. It allocates and frees blocks via metafile block helpers, reports sickness via `XFS_SICK_RG_RMAPBT`, and points to all record/key comparison and verifier routines. `xfs_rtrmapbt_init_cursor` requires the rmap metadata inode lock, allocates from the rtrmap cursor slab, holds the rtgroup, and initializes fork size and level from the inode data fork root.

When `CONFIG_XFS_BTREE_IN_MEM` is enabled, the file also defines an in-memory realtime rmap btree variant. It has a separate verifier that allows construction even when the on-disk feature is not enabled, skips CRC checks, uses generic `xfbtree` allocation/free/set-root operations, and exposes `xfs_rtrmapbt_mem_cursor` plus `xfs_rtrmapbt_mem_init`. This supports userspace or repair-style temporary btrees.

Staged btree commit replaces the real inode fork with a fake fork and logs core/root changes. Capacity helpers compute root and block records, maximum on-disk height, mount-specific maxlevels, btree block count estimates, and reservation sizes. For reflink realtime filesystems, maxlevel computation is based on data device capacity rather than a simple per-block record count because maximum sharing could theoretically create enormous rmap record counts.

Disk/in-memory conversion routines translate between `struct xfs_rtrmap_root` and normal in-memory btree blocks. `xfs_iformat_rtrmap` validates rmap feature presence, level, and fork size before loading. `xfs_iflush_rtrmap` writes the in-memory root back to dinode format. `xfs_rtrmapbt_create` initializes an empty metadata btree root. `xfs_rtrmapbt_init_rtsb` inserts an owner mapping for the realtime superblock extent in rtgroup 0, and `xfs_rtrmap_highest_rgbno` returns the highest group-relative block number tracked in the root high key.
