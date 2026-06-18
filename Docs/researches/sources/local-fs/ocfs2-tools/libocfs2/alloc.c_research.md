# File Research: sources/local-fs/ocfs2-tools/libocfs2/alloc.c

Provides high-level allocation and free operations for OCFS2 userspace: inodes, system inodes, extent blocks, xattr blocks, refcount blocks, indexed-directory roots, and clusters.

Allocation is built on cached chain allocators. `ocfs2_load_allocator()` locates a system inode, reads it into `ocfs2_cached_inode`, primes chain allocator block cache opportunistically, and loads its bitmap. `ocfs2_chain_alloc_with_io()` and `ocfs2_chain_free_with_io()` mutate chain allocator state then immediately write it back.

Inode initialization sets generation, fs generation, block number, suballocator metadata, mode, link count, timestamps, signatures, and layout-specific id2 data. It handles local alloc, chain alloc, dealloc, superblock, inline directory data, and extent-list initialization. Inline xattr space is preserved when zeroing inode id2.

Major APIs: `ocfs2_new_inode`, `ocfs2_new_system_inode`, `ocfs2_delete_inode`, `ocfs2_test_inode_allocated`, `ocfs2_new_extent_block`, `ocfs2_delete_extent_block`, `ocfs2_delete_xattr_block`, `ocfs2_new_refcount_block`, `ocfs2_delete_refcount_block`, `ocfs2_grow_chain_allocator`, `ocfs2_new_dx_root`, `ocfs2_delete_dx_root`, `ocfs2_new_clusters`, `ocfs2_new_specific_cluster`, `ocfs2_free_clusters`, and `ocfs2_test_clusters`.

Notable behavior: inode/extent allocation retries after adding a chain group on `OCFS2_ET_BIT_NOT_FOUND`; cluster allocation ignores local allocs by design; several writeback failures have comments noting incomplete rollback risk; debug mode can create and link a new regular file.
