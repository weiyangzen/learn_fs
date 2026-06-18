# File Research: sources/os/bsd/netbsd-src/sys/ufs/ffs/ffs_vnops.c

This file defines FFS vnode operation vectors and FFS-specific vnode operations for fsync, special-file fsync, reclaim, and getpages sizing. Most normal read/write behavior is included from shared `ufs_readwrite.c`.

Key responsibilities:
- Define operation tables for regular FFS vnodes, special device vnodes, and FIFO vnodes.
- Hook FFS-specific read/write/fsync/reclaim/extattr/ACL operations into NetBSD vnode dispatch.
- Provide WAPBL-aware fsync implementations.
- Free inode/dinode pool storage during reclaim.
- Tell genfs how far writes should extend for fragment/block allocation.

Important data:
- `ffs_vnodeop_entries`: Regular vnode ops, including UFS lookup/create/remove/rename/dir operations, FFS read/write/fsync/reclaim, UFS bmap/strategy, native extattrs, and ACL hooks.
- `ffs_specop_entries`: Special vnode ops with `ffs_spec_fsync`, UFS metadata/EA/ACL hooks, and specfs defaults.
- `ffs_fifoop_entries`: FIFO vnode ops with `ffsext_strategy` to support UFS2 native EA negative block strategy.

Important functions:
- `ffs_spec_fsync`: Calls `spec_fsync`, then updates inode metadata. Under WAPBL it avoids metadata work for data-only/lazy syncs and wraps inode update in a WAPBL transaction.
- `ffs_fsync`: Handles range fsyncs for regular files. It flushes pages, flushes relevant indirect buffers for non-WAPBL range sync, updates inode metadata, optionally flushes WAPBL, and optionally issues device cache sync.
- `ffs_full_fsync`: Full vnode fsync path. Under WAPBL it flushes pages, updates inode metadata, conditionally flushes the log, and waits for output if requested. Without WAPBL it uses `vflushbuf`, `ffs_update`, and optional `DIOCCACHESYNC`.
- `ffs_reclaim`: Frees an inode whose vnode is being reclaimed. It frees unlinked allocated inodes under WAPBL, calls `ufs_reclaim`, returns dinode storage to the correct pool, destroys genfs state, clears vnode data, and returns the inode to `ffs_inode_cache`.
- `ffs_gop_size`: Computes the end offset to write for genfs: fragment-rounded for direct-block growth and block-rounded otherwise.

Important interactions:
- The operation vectors are referenced by `ffs_vfsops.c` during VFS registration and vnode initialization.
- `ffs_read`, `ffs_write`, `ffs_bufrd`, and `ffs_bufwr` come from included shared UFS read/write code.
- Native UFS2 EA ops are supplied by `ffs_extattr.c`; UFS1 fallback depends on UFS extattr configuration.

Notable behavior and risks:
- Range fsync only takes the special range path for regular files with a nonzero range; otherwise it falls back to full fsync.
- WAPBL paths deliberately skip log flushing for syncer/data-only/lazy cases.
- Reclaim temporarily unlocks the vnode before WAPBL/free work, relying on vnode reclaim interlocks.
