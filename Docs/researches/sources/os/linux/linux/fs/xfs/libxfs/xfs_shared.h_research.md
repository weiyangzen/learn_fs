# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_shared.h

## Purpose

`xfs_shared.h` collects declarations and constants shared between kernel and userspace libxfs that do not fit better elsewhere. It exposes verifier ops, btree ops, transaction flags, superblock modification masks, buffer reference priorities, and computed inode geometry.

## Main Content

- Forward-declares common XFS types.
- Declares global `xfs_buf_ops` for AG headers, btrees, quotas, inodes, realtime metadata, superblocks, symlinks, and newer RT rmap/refcount metadata.
- Declares global `xfs_btree_ops` for alloc, inode, bmap, refcount, rmap, realtime rmap, and realtime refcount btrees.
- Provides inline predicates to identify btree op tables.
- Provides optional in-memory rmap/rtrmap btree predicates.
- Declares log reservation sizing helpers.
- Defines transaction flags:
  - Dirty, superblock dirty, permanent reservation, sync, reserve pool, no writecount, freed-block reservation, intent-done, low-mode, RT bitmap locked.
- Defines `xfs_trans_mod_sb` field masks, including realtime group count.
- Defines metadata buffer cache reference values.
- Defines `struct xfs_ino_geometry` with inode-count, cluster, inobt, allocation, alignment, fork offset, flags, and folio-order fields.

## Key Interfaces and Invariants

- Buffer and btree op declarations are shared with userspace repair/check tooling.
- Btree identity helpers use pointer equality against global op tables.
- `XFS_TRANS_LOWMODE` documents allocator behavior for low free-space btree split handling.
- `XFS_TRANS_RTBITMAP_LOCKED` records transaction ownership of realtime bitmap/summary inode locks.
- Inode geometry includes both raw and rounded cluster sizes because validation and runtime allocation need different forms.

## Dependencies

Relies on definitions of buffer ops, btree ops, transaction reservations, and inode/mount types supplied elsewhere in libxfs/kernel builds.
