# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ffs_inode.c

FFS inode update and truncate implementation.

Key responsibilities:
- Implements `ffs_update`, refreshing inode timestamps, clearing lazy/modified flags, skipping writes on read-only filesystems or bad vnodes, maintaining legacy uid/gid fields for old inode formats, reading the inode block, invoking soft updates inode handling when enabled, copying the in-memory dinode to disk, and choosing synchronous or delayed write based on `waitfor`, async mode, and memory pressure.
- Implements `ffs_truncate`, handling both file extension and shrink. It validates length, handles short symlink truncation, integrates quotas, coordinates with soft updates, updates VM/buffer object sizes through `nvextendbuf`/`nvtruncbuf`, allocates the last byte when extending, shrinks partial direct blocks to fragments, writes new inode block pointers before freeing old storage, frees indirect and direct blocks, releases trailing fragments, updates `i_blocks`, and applies quota credits.
- Defines indirect block level constants `SINGLE`, `DOUBLE`, and `TRIPLE`.
- Implements recursive `ffs_indirtrunc`, reading an indirect block by explicit device offset, zeroing unneeded pointers, writing metadata before freeing referenced blocks, recursively freeing lower-level indirect trees, and reporting released block counts.

Dependencies:
- Uses DragonFly VM/buffer interfaces, vnode operations, quota helpers, UFS inode state, FFS filesystem layout macros, and FFS block-free/update helpers.
- Integrates with soft updates through `softdep_setup_freeblocks`, `softdep_slowdown`, and `softdep_update_inodeblock`.

Notable risks:
- Truncate ordering is crash-safety critical: inode pointers are cleared and written before blocks are returned to free maps.
- Partial truncate with soft updates forces fsync in some cases to avoid dangling dependencies.
- Triple-indirect truncation is explicitly noted as untested.
- Manual BIO setup in `ffs_indirtrunc` bypasses normal vnode block mapping, so device offset correctness is essential.
- Block count and quota accounting must match exactly with the blocks/fragments actually freed.
