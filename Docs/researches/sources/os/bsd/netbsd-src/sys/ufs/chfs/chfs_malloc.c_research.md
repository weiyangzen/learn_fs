# File Research: sources/os/bsd/netbsd-src/sys/ufs/chfs/chfs_malloc.c

Purpose: Provides CHFS object allocation wrappers and global pool caches for vnode caches, node refs, flash-node structs, fragments, and temporary read-inode structures.

Key entry points:
- `chfs_alloc_pool_caches`, `chfs_destroy_pool_caches`: initialize/destroy global pool caches.
- `chfs_vnode_cache_alloc/free`: allocate in-memory vnode-cache records.
- `chfs_alloc_refblock`, `chfs_free_refblock`, `chfs_alloc_node_ref`, `chfs_free_node_refs`: manage node-ref blocks chained by sentinel entries.
- `chfs_alloc_dirent/free_dirent`: variable-sized directory entries.
- `chfs_alloc_full_dnode/free_full_dnode`: in-memory full data-node descriptors.
- `chfs_alloc_flash_vnode/dirent/dnode` and free counterparts.
- `chfs_alloc_node_frag/free_node_frag`.
- `chfs_alloc_tmp_dnode/free_tmp_dnode`, `chfs_alloc_tmp_dnode_info/free_tmp_dnode_info`.

Important behavior:
- Node references are allocated in blocks of `REFS_BLOCK_LEN + 1`, where the final element is a link sentinel to the next block.
- `chfs_alloc_node_ref` attaches the first refblock to an eraseblock and advances through block-local node refs in physical write order.
- Vnode cache allocation initializes list sentinels by pointing `v`, `dirents`, and `dnode` at the cache object itself.
- Dirents are allocated with flexible trailing name storage.

Dependencies:
- Uses NetBSD `pool_cache` and `kmem`.
- Relied on by scan, write, GC, vnode-cache, and read-inode paths.

Research notes:
- `chfs_free_node_refs` walks sentinel-linked refblocks and frees each refblock.
- Allocation wrappers mostly use `PR_WAITOK`/`KM_SLEEP`, so callers generally assume allocation succeeds or blocks.
