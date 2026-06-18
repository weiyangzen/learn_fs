# File Research: sources/os/bsd/netbsd-src/sys/ufs/chfs/chfs_write.c

Purpose: Serializes CHFS vnode metadata, directory entries, data nodes, hard links, and unlink records to flash as append-only nodes.

Key entry points:
- `chfs_write_flash_vnode`: writes a `CHFS_NODETYPE_VNODE`.
- `chfs_write_flash_dirent`: writes a `CHFS_NODETYPE_DIRENT` plus padded name payload.
- `chfs_write_flash_dnode`: writes a `CHFS_NODETYPE_DATA` plus padded data payload.
- `chfs_do_link`: writes metadata/dirent changes for adding a directory entry to an existing inode.
- `chfs_do_unlink`: writes deletion dirent and obsoletes/removes old vnode/data/dirent node refs.

Important behavior:
- Root vnode metadata is in-memory only and skipped by `chfs_write_flash_vnode`.
- Each write builds header/node/data CRCs, reserves space, allocates a new node ref in `chm_nextblock`, updates free/used accounting, writes via the write buffer, and updates vnode-cache chains.
- Normal writes trigger GC before reserving space; GC relocation uses `ALLOC_GC`.
- Write errors mark attempted bytes dirty and retry once before returning EIO.
- Data-node writes replace old fragment/node refs when `fd->nref` is already set.
- Unlink kills the inode fragment tree, decrements link count, writes a deletion dirent with inode number zero, removes old dirent/vnode/data refs, and updates parent link count.

Dependencies:
- Uses space reservation from `chfs_nodeops.c`, write buffer from `chfs_wbuf.c`, fragment helpers from `chfs_readinode.c`, and allocation wrappers from `chfs_malloc.c`.

Research notes:
- `chfs_write_flash_dirent` allocates a padded name buffer but does not free it in this function.
- Some fields are stored with endian conversion while a few dirent fields are assigned without explicit conversion, matching existing code but worth noting for portability review.
- Link/unlink comments include TODOs for error handling.
