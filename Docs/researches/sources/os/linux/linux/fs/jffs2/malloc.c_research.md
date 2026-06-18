# File Research: sources/os/linux/linux/fs/jffs2/malloc.c

This file centralizes allocation and freeing of JFFS2 in-core objects through slab caches and targeted `kmalloc()` allocations.

`jffs2_create_slab_caches()` creates caches for full dnodes, raw dirents, raw inodes, temporary dnode info, raw node-ref blocks, node fragments, inode caches, and optional xattr datum/ref objects. Failure unwinds through `jffs2_destroy_slab_caches()`. `jffs2_destroy_slab_caches()` destroys all caches.

Allocation/free wrappers exist for `jffs2_full_dirent`, `jffs2_full_dnode`, `jffs2_raw_dirent`, `jffs2_raw_inode`, `jffs2_tmp_dnode_info`, `jffs2_node_frag`, and `jffs2_inode_cache`, with memory-allocation debug logging. Full dirents are variable-sized and allocated by `kmalloc(sizeof(...) + namesize)`.

Raw node refs are allocated in blocks. `jffs2_alloc_refblock()` initializes `REFS_PER_BLOCK` entries as `REF_EMPTY_NODE` and the final entry as `REF_LINK_NODE`. `jffs2_prealloc_raw_node_refs()` reserves a requested number of empty refs in an eraseblock’s ref chain, allocating linked refblocks as needed and recording `jeb->allocated_refs`.

Optional xattr allocation helpers zero-initialize xattr objects, set their raw-node class, initialize common fields, and free through their slabs.

Key dependencies: `nodelist.h` object definitions and debug allocation macros.

Important invariant: writes must preallocate enough raw node refs before linking physical nodes; `jffs2_link_node_ref()` later consumes `jeb->allocated_refs`.
