# File Research: sources/local-fs/xfsprogs/libxfs/xfs_rtrefcount_btree.c

This file implements the realtime refcount btree, an inode-rooted metadata btree used to track sharing/refcount records for realtime extents. It mirrors the regular refcount btree but stores its root in a per-rtgroup metadata inode.

The btree cursor operations define how refcount keys, records, and pointers behave. `xfs_rtrefcountbt_dup_cursor` recreates a cursor for the same transaction and rtgroup. Min/max record functions use the inode root fork size at the root level and mount precomputed `m_rtrefc_mnr/mxr` for all other levels. `xfs_rtrefcountbt_droot_maxrecs` computes capacity of the on-disk dinode root format, which differs from the in-memory btree root.

Record/key initialization encodes `struct xfs_refcount_irec` into disk records. The startblock is encoded with the refcount domain via `xfs_refcount_encode_startblock`; high keys cover the last block of a refcount extent. Key comparisons are by encoded startblock. Record ordering requires non-overlap: previous start plus length must be less than or equal to next start.

Buffer verification requires the refcount/reflink feature, validates v5 long-format btree headers with unknown owner, checks level against `m_rtrefc_maxlevels`, checks block structure against the per-level max record count, and enforces CRCs on read/write through `xfs_rtrefcountbt_buf_ops`.

The btree ops table `xfs_rtrefcountbt_ops` marks this as an inode btree with inode-root records. Allocation/free are delegated to metafile block helpers because the btree lives in metadata files, not free-space owned AG blocks. It also wires sickness reporting to `XFS_SICK_RG_REFCNTBT`.

Root reallocation is specialized because inode-root pointers are not laid out immediately after the header in the same way as leaf records. `xfs_rtrefcountbt_broot_realloc` expands or shrinks the root and moves node pointers with `xfs_rtrefcountbt_move_ptrs` when needed. The code asserts that the converted on-disk root fits inside the inode fork.

`xfs_rtrefcountbt_init_cursor` requires the refcount metadata inode to be locked, allocates a cursor from the rtrefcount cursor slab, points it at the metadata inode, holds the rtgroup, and initializes cursor levels/fork geometry from the inode data fork root.

Staging support is represented by `xfs_rtrefcountbt_commit_staged_btree`, which replaces the real fork with an ifakeroot fork, sets `i_projid` to the rtgroup number, logs core and data-root changes, and commits the fake root. The actual stage-cursor declaration lives in the header and is implemented elsewhere.

Geometry helpers compute max records, maximum on-disk height, mount-specific maximum height, maximum reserve size, and reserve blocks. Realtime refcount reserves are present only with `xfs_has_rtreflink`. The maximum height is constrained by both data-device capacity and records needed for one record per rt extent in a group, plus one level for the inode root.

Disk/in-memory root conversion functions translate between `struct xfs_rtrefcount_root` in the dinode data fork and a normal in-memory `struct xfs_btree_block`. `xfs_iformat_rtrefcount` validates feature presence, root level, and root size before allocating the in-memory root. `xfs_iflush_rtrefcount` converts the in-memory root back to disk at inode flush. `xfs_rtrefcountbt_create` initializes an empty `XFS_DINODE_FMT_META_BTREE` metadata inode root and logs it.
